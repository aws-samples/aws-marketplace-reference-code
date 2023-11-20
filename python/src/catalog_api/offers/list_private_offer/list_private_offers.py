"""
Purpose
Shows how to use the AWS SDK for Python (Boto3) for listing offers in the AWS Marketplace Catalog
CAPI-40
"""
import json
import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# constants
MAX_PAGE_RESULTS = 10
ENTITY_TYPE = "Offer"


def pretty_print(response):
    json_object = json.dumps(response, indent=4)
    print(json_object)


def list_private_offers(mp_client):
    """
    This method retrieves list of all Private Offers for this account.
    """
    EntitySummaryList = []
    try:
        response = mp_client.list_entities(
            Catalog="AWSMarketplace",
            EntityType=ENTITY_TYPE,
            FilterList=[
                {
                    "Name": "Visibility",
                    "ValueList": [
                        "Private",
                    ],
                },
            ],
            MaxResults=MAX_PAGE_RESULTS,  # default 20 results shall be returned.
        )
    except ClientError:
        logger.exception("Error: Couldn't get list of Offers.")
        raise

    EntitySummaryList.extend(response["EntitySummaryList"])
    logger.info("Number of results in first iteration: %d " % len(EntitySummaryList))
    # Get subsequent pages of results if previous response contained a NextToken
    while "NextToken" in response:
        try:
            logger.info("Getting Next Token results: %s " % response["NextToken"])
            response = mp_client.list_entities(
                Catalog="AWSMarketplace",
                EntityType=ENTITY_TYPE,
                FilterList=[
                    {
                        "Name": "Visibility",
                        "ValueList": [
                            "Private",
                        ],
                    },
                ],
                MaxResults=MAX_PAGE_RESULTS,
                NextToken=response["NextToken"],
            )
        except ClientError as e:
            logger.error("Could not complete list_entities request.")
            raise

        EntitySummaryList.extend(response["EntitySummaryList"])
        logger.info(
            "Number of results in the current iteration: %d "
            % len(response["EntitySummaryList"])
        )

    return EntitySummaryList


def get_offer_details(mp_client, offer):
    """
    Describe the details of the Offer.
    """
    try:
        response = mp_client.describe_entity(
            Catalog="AWSMarketplace", EntityId=offer["EntityId"]
        )

        return response
    except ClientError:
        logger.exception("Error: Couldn't get details of the Offer.")
        raise


def usage_demo():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    print("-" * 88)
    print("Demo  - List Private offers.")
    print("-" * 88)

    mp_client = boto3.client("marketplace-catalog")

    # Get list of all Offers.
    private_offers = list_private_offers(mp_client)
    count = len(private_offers)

    logger.info("Number of Offers: %d " % count)
    offercounter = 0
    # Display details of each Offer.
    for offer in private_offers:
        print("-" * 88)
        offercounter += 1
        print("Displaying Offer details for Offer# %d" % offercounter)
        entity = get_offer_details(mp_client, offer)
        pretty_print(entity)

    print("-" * 88)


if __name__ == "__main__":
    usage_demo()
