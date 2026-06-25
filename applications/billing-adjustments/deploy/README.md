# Deploy the Billing Adjustments app into an AWS account (Option 3)

This deploys the same web UI as a small service **inside an AWS account** (the
partner's own account) using **AWS App Runner**. The key benefits over shipping a
binary or collecting credentials:

- **No credentials are ever entered.** The app uses an attached IAM role
  (`MANAGED_CREDENTIALS=true`), so it acts with the account's own permissions.
- **Least privilege.** The role only allows the four billing-adjustment actions.
- **Access controlled.** A shared password (required) gates the UI, since the app
  can act via the role.
- **Just a URL for users.** App Runner provides an HTTPS endpoint — nothing to
  install on the user's machine, works on any device with a browser.

> **Common information** — input file format, currencies, run-output statuses,
> idempotency, error codes, and quotas — is in the **[main README](../README.md)**.
> This guide covers only deployment.

## What gets created

- An **App Runner service** running the app container (HTTPS URL, auto-scaling).
- An **IAM instance role** with only:
  - `aws-marketplace:ListAgreementInvoiceLineItems`
  - `aws-marketplace:BatchCreateBillingAdjustmentRequest`
  - `aws-marketplace:GetBillingAdjustmentRequest`
  - `aws-marketplace:ListBillingAdjustmentRequests`
- (Private-image option only) an ECR access role for App Runner to pull the image.

> **Verify the IAM action names.** These four actions use the `aws-marketplace:`
> namespace (the Agreement Service namespace). Confirm the exact action names for
> the billing-adjustment operations against the AWS *Service Authorization
> Reference* for your account/region before relying on the policy in production;
> if an action name differs, update `cloudformation.yaml` (same-account) and/or
> `cross-account-role-target.yaml` (cross-account).

## Prerequisites

- A container engine — **Docker (with buildx)** or **Finch** — and the AWS CLI, on a
  machine with permissions to push to ECR and deploy CloudFormation in the target
  account. `publish-image.sh` auto-detects which engine to use (override with
  `CONTAINER_ENGINE=docker|finch`). For Finch, start its VM first: `finch vm start`.
- The target account must have access to the Marketplace Agreement billing APIs.

## Step 1 — Build and push the image

From the repo root (the folder containing `webapp/` and `deploy/`):

```bash
./deploy/publish-image.sh
```

This creates a private ECR repo (if needed), builds the image for `linux/amd64`,
pushes it, and prints the **ImageUri** to use next.

> Prefer a public image (so multiple partner accounts can pull the same one)?
> Push to a public ECR gallery repo you own and deploy with
> `ImageRepositoryType=ECR_PUBLIC`. Otherwise use the private flow above with
> `ImageRepositoryType=ECR`.

## Step 2 — Deploy the stack

```bash
aws cloudformation deploy \
  --template-file deploy/cloudformation.yaml \
  --stack-name billing-adjustments \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
      ImageUri=<IMAGE_URI_FROM_STEP_1> \
      ImageRepositoryType=ECR \
      AccessPassword='<choose-a-strong-password>'
```

## Cross-account deployment (app in your account, agreements in another)

Use this when you want to run the app in **your own account (the "app account")**
but act on agreements owned by a **different account (the "data account")** — for
example, deploying under your Isengard account while testing against another
account's billing refunds.

The app assumes a role in the data account at runtime and uses its temporary
credentials (auto-refreshed hourly). No long-term keys anywhere.

**Step A — In the DATA account** (the one that owns the agreements), deploy the
cross-account role. Pick a strong external ID and note your app account's ID:

```bash
aws cloudformation deploy \
  --template-file deploy/cross-account-role-target.yaml \
  --stack-name billing-adjustments-xacct-role \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
      AppAccountId=<APP_ACCOUNT_ID> \
      ExternalId='<a-strong-shared-secret>'
```

Get the role ARN it created:

```bash
aws cloudformation describe-stacks \
  --stack-name billing-adjustments-xacct-role \
  --query "Stacks[0].Outputs[?OutputKey=='RoleArn'].OutputValue" --output text
```

**Step B — In the APP account**, deploy the app stack with the assume-role params:

```bash
aws cloudformation deploy \
  --template-file deploy/cloudformation.yaml \
  --stack-name billing-adjustments \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
      ImageUri=<IMAGE_URI> \
      ImageRepositoryType=ECR \
      AccessPassword='<choose-a-strong-password>' \
      AssumeRoleArn='<ROLE_ARN_FROM_STEP_A>' \
      AssumeRoleExternalId='<same-shared-secret-as-step-A>'
```

When `AssumeRoleArn` is set, the app's own role gets only `sts:AssumeRole` on that
ARN — the billing-adjustment permissions live on the role in the data account.

**(Optional) Tighten the trust.** After Step B, the app stack outputs `AppRoleArn`.
Re-deploy the data-account role with `AppRoleArn=<that ARN>` so that *only* the
app's role (not the whole app account) can assume it.

## Step 3 — Get the URL and share it

```bash
aws cloudformation describe-stacks \
  --stack-name billing-adjustments \
  --query "Stacks[0].Outputs[?OutputKey=='AppUrl'].OutputValue" \
  --output text
```

Give users the URL and the access password. They open the URL, sign in, upload a
CSV, and run a dry run / live run. No credentials, no install.

## Updating the app

Re-run `./deploy/publish-image.sh` to push a new image, then either redeploy the
stack or trigger a new App Runner deployment:

```bash
aws apprunner start-deployment --service-arn <ServiceArn-from-stack-outputs>
```

## Tear down

```bash
aws cloudformation delete-stack --stack-name billing-adjustments
```

## Security notes

- **Password handling.** For simplicity the access password is passed as an App
  Runner runtime environment variable. To harden, store it in AWS Secrets Manager
  and reference it via App Runner `RuntimeEnvironmentSecrets` instead of a plain
  env var.
- **Session secret.** The app generates a random Flask session key at startup if
  `FLASK_SECRET_KEY` is not set, so user sessions reset when the service restarts.
  Set `FLASK_SECRET_KEY` (ideally from Secrets Manager) for stable sessions.
- **Network exposure.** App Runner endpoints are public by default (protected only
  by the app password). For tighter control, front it with a WAF or use App Runner
  VPC ingress / a private setup.
- **Job data.** Uploaded files and per-job outputs are written to the container's
  local disk and are lost when the instance is replaced. That's fine for this
  workflow (results are downloaded right after a run). For durable history, mount
  or sync outputs to S3.
- **This is an interim deployment.** It approximates a future native storefront
  feature. The engine lives in the decoupled `core/` package so it can be reused by
  whatever hosts it next.
