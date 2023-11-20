"""
Purpose
Shows how to use the AWS SDK for Python (Boto3) to search for agreement by product id
AG-02
"""

import logging

import boto3
import utils.helpers as helper
from botocore.exceptions import ClientError

# product id to search by
resourceId = "prod-1111111111111"

MAX_PAGE_RESULTS = 10

logger = logging.getLogger(__name__)


def get_agreements(mp_client):
    AgreementSummaryList = []
    partyTypes = ["Proposer"]
    for value in partyTypes:
        try:
            agreement = mp_client.search_agreements(
                catalog="AWSMarketplace",
                maxResults=MAX_PAGE_RESULTS,
                filters=[
                    {"name": "PartyType", "values": [value]},
                    {"name": "ResourceIdentifier", "values": [resourceId]},
                    {"name": "AgreementType", "values": ["PurchaseAgreement"]},
                ],
            )
        except ClientError as e:
            logger.error("Could not complete list_entities request.")
            raise

        AgreementSummaryList.extend(agreement["agreementViewSummaries"])

        while "nextToken" in agreement:
            try:
                agreement = mp_client.search_agreements(
                    catalog="AWSMarketplace",
                    maxResults=MAX_PAGE_RESULTS,
                    nextToken=agreement["nextToken"],
                    filters=[
                        {"name": "PartyType", "values": [value]},
                        {"name": "ResourceIdentifier", "values": [resourceId]},
                        {"name": "AgreementType", "values": ["PurchaseAgreement"]},
                    ],
                )
            except ClientError as e:
                logger.error("Could not complete search_agreements request.")
                raise

            AgreementSummaryList.extend(agreement["agreementViewSummaries"])

    return AgreementSummaryList


def usage_demo():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    print("-" * 88)
    print("Looking for an agreement in the AWS Marketplace Catalog.")
    print("-" * 88)

    mp_client = boto3.client("marketplace-agreement")

    helper.pretty_print_datetime(get_agreements(mp_client))


if __name__ == "__main__":
    usage_demo()
