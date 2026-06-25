# Cross-account deployment walkthrough

Use this when the app runs in **one AWS account** but acts on agreements owned by a
**different account**. The app uses an IAM role in the app account, which assumes a
role in the data account; the assumed role's temporary credentials are used to call
the billing-adjustment APIs and are refreshed automatically.

Two accounts in this example (replace with your own 12-digit IDs):

| Role in this guide | Meaning | Placeholder |
|--------------------|---------|-------------|
| **Data account**   | Owns the agreements / billing data | `DATA_ACCOUNT_ID` |
| **App account**    | Runs the app (App Runner, IAM)     | `APP_ACCOUNT_ID`  |

Region used below: `us-east-1` (change if needed).

> Tip: keep two named CLI profiles, e.g. `--profile data-account` and
> `--profile app-account`, or switch with `AWS_SHARED_CREDENTIALS_FILE=...`.
> Each command below shows which account it runs against.

---

## Step 0 — Pick a shared secret (external ID)

The external ID prevents the "confused deputy" problem. Generate one and keep it:

```bash
python -c "import secrets; print(secrets.token_hex(16))"
# e.g. -> 7f3c...  (save this; you'll use it in Step 1 and Step 3)
```

## Step 1 — Create the cross-account role in the DATA account

This role has the least-privilege billing-adjustment permissions and trusts the app
account (plus the external ID) to assume it.

```bash
# Runs against the DATA account
aws cloudformation deploy \
  --template-file deploy/cross-account-role-target.yaml \
  --stack-name billing-adjustments-xacct-role \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1 \
  --profile data-account \
  --parameter-overrides \
      AppAccountId=APP_ACCOUNT_ID \
      ExternalId='<external-id-from-step-0>'
```

Get the role ARN it created (you'll pass this to the app in Step 3):

```bash
aws cloudformation describe-stacks \
  --stack-name billing-adjustments-xacct-role \
  --region us-east-1 --profile data-account \
  --query "Stacks[0].Outputs[?OutputKey=='RoleArn'].OutputValue" --output text
# -> arn:aws:iam::DATA_ACCOUNT_ID:role/billing-adjustments-cross-account
```

## Step 2 — Build and push the app image (in the APP account)

```bash
# Runs against the APP account. From the kit root (folder with webapp/ and deploy/).
./deploy/publish-image.sh                       # uses the current AWS profile/creds
# or set the profile explicitly:
AWS_PROFILE=app-account ./deploy/publish-image.sh
```

The script prints the image URI, e.g.
`APP_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/billing-adjustments:latest`.

> **No `docker buildx`?** Some Docker setups (e.g. Homebrew docker + colima) don't
> have the buildx plugin. In that case build/push manually instead of the script:
> ```bash
> IMAGE_URI=APP_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/billing-adjustments:latest
> aws ecr create-repository --repository-name billing-adjustments --region us-east-1 --profile app-account 2>/dev/null
> aws ecr get-login-password --region us-east-1 --profile app-account \
>   | docker login --username AWS --password-stdin APP_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
> docker build --platform linux/amd64 -f deploy/Dockerfile -t "$IMAGE_URI" .
> docker push "$IMAGE_URI"
> ```
> App Runner expects a `linux/amd64` image, hence the `--platform` flag.

## Step 3 — Deploy the app in the APP account with assume-role

```bash
# Runs against the APP account
aws cloudformation deploy \
  --template-file deploy/cloudformation.yaml \
  --stack-name billing-adjustments \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1 \
  --profile app-account \
  --parameter-overrides \
      ImageUri='<IMAGE_URI_FROM_STEP_2>' \
      ImageRepositoryType=ECR \
      AccessPassword='<choose-a-strong-password>' \
      AssumeRoleArn='<ROLE_ARN_FROM_STEP_1>' \
      AssumeRoleExternalId='<external-id-from-step-0>'
```

When `AssumeRoleArn` is set, the app's own role only gets `sts:AssumeRole` on that
ARN — the billing-adjustment permissions live on the data-account role.

## Step 4 — Get the URL and test

```bash
aws cloudformation describe-stacks \
  --stack-name billing-adjustments \
  --region us-east-1 --profile app-account \
  --query "Stacks[0].Outputs" --output table
```

Open the `AppUrl`, sign in with the access password, upload `sample_input.csv` (or
real data), keep **Dry run** checked, and **Start job**. No AWS credentials are
requested — the app assumes the data-account role automatically. A successful dry
run validates the invoices against the data account's agreements.

## Step 5 (optional) — Tighten the trust

The app stack outputs `AppRoleArn`. Re-deploy the data-account role so that *only*
that role (not the whole app account) may assume it:

```bash
# Runs against the DATA account
aws cloudformation deploy \
  --template-file deploy/cross-account-role-target.yaml \
  --stack-name billing-adjustments-xacct-role \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1 --profile data-account \
  --parameter-overrides \
      AppAccountId=APP_ACCOUNT_ID \
      ExternalId='<external-id-from-step-0>' \
      AppRoleArn='<AppRoleArn-from-step-4-outputs>'
```

## Teardown

```bash
# APP account
aws cloudformation delete-stack --stack-name billing-adjustments --region us-east-1 --profile app-account
# DATA account
aws cloudformation delete-stack --stack-name billing-adjustments-xacct-role --region us-east-1 --profile data-account
```

## How it works (quick reference)

```
[App account]                              [Data account]
App Runner service                         Cross-account role
  └─ app instance role                       └─ aws-marketplace:ListAgreementInvoiceLineItems
       (sts:AssumeRole on the   ───assume──▶      aws-marketplace:BatchCreateBillingAdjustmentRequest
        data-account role)        + ExternalId     aws-marketplace:GetBillingAdjustmentRequest
                                                 trust: APP_ACCOUNT_ID + ExternalId
```

The assumed-role credentials are temporary and auto-refresh before they expire, so
long-running jobs continue without interruption.
