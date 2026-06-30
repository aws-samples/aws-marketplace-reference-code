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

## Architecture and roles

![Deployment architecture: the deployer builds/pushes to Amazon ECR and runs CloudFormation, which creates the app role, the ECR-access role, and the App Runner service (managed compute, no EC2). The App Runner task assumes the app role to call the AWS Marketplace Agreement APIs, or assumes a cross-account role in the DATA account.](deploy.png)

| Identity | What it is | Assumed by / trust | Permissions |
|----------|------------|--------------------|-------------|
| **Deployer principal** | You at deploy time (`publish-image.sh` + `cloudformation deploy`) | your own login | ECR push, CloudFormation, IAM role create/pass, App Runner (the deployer policy under *Who runs the deployment*). **No `aws-marketplace` perms.** |
| **`billing-adjustments-app-role`** | The running app's identity | `tasks.apprunner.amazonaws.com` | Same-account: the 4 `aws-marketplace` actions. Cross-account: only `sts:AssumeRole` on the target role. |
| **`billing-adjustments-ecr-access-role`** | Lets App Runner pull the private image | `build.apprunner.amazonaws.com` | Managed `AWSAppRunnerServicePolicyForECRAccess` (private ECR only). |
| **`BillingAdjustmentsXAcctRole`** (DATA account) | Holds the real perms where the agreements live | APP account principal + `ExternalId` | The 4 `aws-marketplace` actions. |

Two things to note: the **deployer is not the app role** (the deployer *creates* and
`PassRole`s it, but never runs as it), and **App Runner is fully managed** — your
container runs on AWS-managed compute with no EC2 instance in your account.

## Prerequisites

- A container engine — **Docker (with buildx)** or **Finch** — and the AWS CLI, on a
  machine with permissions to push to ECR and deploy CloudFormation in the target
  account. `publish-image.sh` auto-detects which engine to use (override with
  `CONTAINER_ENGINE=docker|finch`). For Finch, start its VM first: `finch vm start`.
- The target account must have access to the Marketplace Agreement billing APIs.

## Who runs the deployment (deployer permissions)

Deploying is a **one-time, elevated operation** — it creates IAM roles and an App
Runner service (and, for a private image, pushes to ECR). This is separate from
*running* the app: the running service uses only the least-privilege role the stack
creates, never the deployer's permissions.

You have two options:

1. **A cloud / AWS administrator deploys it.** Simplest — an admin typically already
   has the required rights. Recommended if you just want it stood up.
2. **Delegate to a specific person or role** that has the least-privilege deployer
   policy below attached. Use this when you don't want to hand out admin, or for a
   security review of exactly what the deployment touches. Note it contains **no
   `aws-marketplace:` permissions** — those live only on the app role the stack
   creates, not on the deployer.

<details>
<summary><strong>Least-privilege deployer IAM policy</strong> (click to expand)</summary>

This policy uses **example values** — account `111122223333` and region `us-east-1`.
Replace `111122223333` with the account you're deploying into (find it with
`aws sts get-caller-identity --query Account --output text`). Leave `us-east-1` unless
you deploy ECR/App Runner in another region — the Marketplace API itself is always
`us-east-1` regardless of where you host the app. Keep `billing-adjustments` unless you
change the `ServiceName` parameter. For a **public image**
(`ImageRepositoryType=ECR_PUBLIC`) you can drop the two `Ecr*` statements and the
`billing-adjustments-ecr-access-role` entry from `PassRole` (no image build/push and no
ECR access role).

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Sid": "EcrAuthToken", "Effect": "Allow", "Action": "ecr:GetAuthorizationToken", "Resource": "*" },
    {
      "Sid": "EcrPushImage",
      "Effect": "Allow",
      "Action": [
        "ecr:DescribeRepositories", "ecr:CreateRepository", "ecr:BatchCheckLayerAvailability",
        "ecr:InitiateLayerUpload", "ecr:UploadLayerPart", "ecr:CompleteLayerUpload",
        "ecr:PutImage", "ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"
      ],
      "Resource": "arn:aws:ecr:us-east-1:111122223333:repository/billing-adjustments"
    },
    {
      "Sid": "CloudFormationStack",
      "Effect": "Allow",
      "Action": [
        "cloudformation:CreateStack", "cloudformation:UpdateStack", "cloudformation:DeleteStack",
        "cloudformation:DescribeStacks", "cloudformation:DescribeStackEvents",
        "cloudformation:ListStackResources", "cloudformation:GetTemplate",
        "cloudformation:CreateChangeSet", "cloudformation:DescribeChangeSet",
        "cloudformation:ExecuteChangeSet", "cloudformation:DeleteChangeSet"
      ],
      "Resource": "arn:aws:cloudformation:us-east-1:111122223333:stack/billing-adjustments/*"
    },
    {
      "Sid": "CloudFormationValidate",
      "Effect": "Allow",
      "Action": ["cloudformation:ValidateTemplate", "cloudformation:GetTemplateSummary"],
      "Resource": "*"
    },
    {
      "Sid": "IamRolesForStack",
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole", "iam:DeleteRole", "iam:GetRole", "iam:GetRolePolicy",
        "iam:PutRolePolicy", "iam:DeleteRolePolicy", "iam:AttachRolePolicy",
        "iam:DetachRolePolicy", "iam:ListRolePolicies", "iam:ListAttachedRolePolicies",
        "iam:TagRole", "iam:UntagRole"
      ],
      "Resource": "arn:aws:iam::111122223333:role/billing-adjustments-*"
    },
    {
      "Sid": "IamPassRoleToAppRunner",
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": [
        "arn:aws:iam::111122223333:role/billing-adjustments-app-role",
        "arn:aws:iam::111122223333:role/billing-adjustments-ecr-access-role"
      ]
    },
    {
      "Sid": "AppRunnerServiceLinkedRole",
      "Effect": "Allow",
      "Action": "iam:CreateServiceLinkedRole",
      "Resource": "arn:aws:iam::111122223333:role/aws-service-role/apprunner.amazonaws.com/*",
      "Condition": { "StringEquals": { "iam:AWSServiceName": "apprunner.amazonaws.com" } }
    },
    {
      "Sid": "AppRunnerService",
      "Effect": "Allow",
      "Action": [
        "apprunner:CreateService", "apprunner:UpdateService", "apprunner:DeleteService",
        "apprunner:DescribeService", "apprunner:ListServices", "apprunner:ListOperations",
        "apprunner:DescribeOperation", "apprunner:StartDeployment", "apprunner:TagResource",
        "apprunner:ListTagsForResource"
      ],
      "Resource": "*"
    },
    { "Sid": "StsIdentity", "Effect": "Allow", "Action": "sts:GetCallerIdentity", "Resource": "*" }
  ]
}
```
</details>

> **Cross-account:** the person deploying `cross-account-role-target.yaml` in the
> **DATA account** (example: `444455556666`) needs CloudFormation on that stack plus
> `iam:CreateRole` / `PutRolePolicy` / `GetRole` / `DeleteRole` on
> `arn:aws:iam::444455556666:role/BillingAdjustmentsXAcctRole` — a separate, smaller
> policy in that account.

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
