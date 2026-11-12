![image](images/AWS-Marketplace-logo.png)



# AWS Marketplace API Reference Code Library

The AWS Marketplace Catalog APIs and Agreements APIs provide API interfaces to manage AWS Marketplace for a proposer's or acceptor's
AWS organization or AWS account. More information about Catalog API is available [here](https://docs.aws.amazon.com/marketplace-catalog/latest/api-reference/welcome.html).  Information about Agreement API is available [here](https://docs.aws.amazon.com/marketplace-agreements/latest/api-reference/welcome.html)

This repository hosts a variety of useful reference code examples to help partners automate their workflows with the
AWS Marketplace Catalog API and Agreements API. Reference code examples found in this repository
are written in [Python 3.x](./python) and [Java](./java).

## Getting started

You will need to have credentials to an [AWS seller account](https://docs.aws.amazon.com/marketplace/latest/userguide/user-guide-for-sellers.html)
or [AWS buyer account](https://docs.aws.amazon.com/marketplace/latest/buyerguide/what-is-marketplace.html)
 and a [Git client](https://git-scm.com/downloads) installed

### Clone the Git repository to your local workstation:
```
git clone git@github.com:aws-samples/aws-marketplace-reference-code.git
```

Instructions on setting up your environment to run the Python examples can found in the [Python sub-folder](./python) of this repository.

## Applications

In addition to the language-specific reference snippets, the [`applications/`](./applications) folder
contains complete, runnable tools built on these APIs. Each application is self-contained,
with its own README and dependencies.

| Application | Description |
|-------------|-------------|
| [Bulk billing adjustments](./applications/billing-adjustments/README.md) | Process bulk billing adjustments (refunds) for AWS Marketplace sellers — validate invoices, submit adjustments in batches, reconcile a refund file against the service, and track status. Includes a shared engine, a CLI, a web UI, and AWS deployment templates. |

## Postman collections

The [`PostmanCollections/postman/collections/`](./PostmanCollections/postman/collections) folder contains the
AWS Marketplace Postman collections that are published in the AWS Marketplace workspace on the Postman API Network:

- AWS Marketplace Catalog API
- AWS Marketplace Agreement API
- AWS Marketplace Discovery API
- AWS Marketplace Self-service Cancellation And Billing Adjustment
- AWS Marketplace Labs by Use Cases

When a change to a collection is merged to `main`, a GitHub Actions workflow updates the published collection.
To change a collection, open a pull request that edits its JSON file instead of editing the collection in Postman.

If a published collection was changed in Postman since the last update, the workflow stops without overwriting
those changes. To keep them, run `python3 .github/scripts/postman_sync.py pull` with `POSTMAN_API_KEY` set, and
commit the updated JSON files in a pull request.

### Submit defects & questions
If you find any defects with the APIs, need help troubleshooting, or have general questions or feedback, [use this form to contact us](https://aws.amazon.com/marketplace/management/contact-us/)

## License

This library is licensed under the MIT-0 License. See the [LICENSE file](LICENSE)..

