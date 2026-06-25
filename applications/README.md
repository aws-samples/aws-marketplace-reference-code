# Applications

This folder holds **complete, runnable applications** built on the AWS Marketplace
Catalog and Agreement APIs.

It is separate from the language folders (`java/`, `javascript/`, `python/`), which
contain small, single-purpose **reference snippets** you copy from. The applications
here are self-contained tools: each has its own `README.md`, its own dependencies
(`requirements.txt`), and may bundle a CLI, a web UI, and deployment templates. You
run them as-is or adapt them, rather than lifting a single function.

## Available applications

| Application | Description |
|-------------|-------------|
| [billing-adjustments](./billing-adjustments/README.md) | Bulk billing adjustments (refunds) for AWS Marketplace sellers via the Agreement billing-adjustment APIs. Validate invoices, submit adjustments in batches, auto-separate invalid/duplicate rows, reconcile a refund file against the service, and track status. Includes a shared engine, a CLI, a Flask web UI, and AWS deployment templates. |

## Conventions

- Each application lives in its own subfolder and is **self-contained** — it manages
  its own dependencies and does not rely on the shared `python/` packaging.
- Applications must ship with **dummy sample data only**. Real customer data,
  credentials, and generated run outputs are kept out of git (see each app's
  `.gitignore`).
- This code is licensed under the same terms as the rest of this repository — see the
  root [LICENSE](../LICENSE) (MIT-0).
