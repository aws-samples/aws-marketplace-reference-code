# Partner kit — source + how to deliver

This folder holds the **authored** files for the external-partner deliverable. The
deliverable itself (a zip) is **generated** from these files plus the app source.

## Tracked sources (in this folder)

```
START-HERE.md                 <- engineer instructions (run locally OR deploy to AWS)
CROSS-ACCOUNT-WALKTHROUGH.md  <- step-by-step for "app in one account, data in another"
sample_input.csv              <- example input file (dummy data) showing the format
README.md                     <- this file (also copied into the built kit as resource/README.md)
```

The application source lives at the repo root in `webapp/` and `deploy/`.

## Build the deliverable

From the repo root:

```bash
./build-partner-kit.sh
```

This produces (both gitignored — regenerate any time):

```
resource/BillingAdjustments-Partner-Kit.zip   <- the file you deliver
resource/partner-kit/                          <- unzipped contents, for review
```

## How to deliver

- **Do not commit the zip** — it's a binary build artifact that goes stale. Rebuild
  it with the script whenever the sources change.
- Send the zip to the partner's engineer via a **secure channel** — an S3 pre-signed
  link or an internal file share. Avoid plain email for large/executable-looking files.
- For external partners, the **recommended** path is deploying the app into their AWS
  account (App Runner) per `deploy/README.md`; the zip is for engineers who want to
  run or deploy it themselves.

## What's inside the built kit

- `README.md` — the **main README** (common reference: input file format, currencies,
  run-output statuses, idempotency, error codes, quotas)
- `START-HERE.md`, `CROSS-ACCOUNT-WALKTHROUGH.md`, `sample_input.csv`
- `webapp/` — the web application (source) + README + double-click launchers
- `cli/` — the command-line scripts + README (for engineers who prefer the CLI)
- `deploy/` — Dockerfile + CloudFormation templates
- `requirements.txt`

It contains **no credentials and no real account/agreement data** — the sample uses
placeholder values only.
