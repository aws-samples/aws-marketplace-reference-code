"""
Purpose
Shows how to use the AWS SDK for Python (Boto3) to update the expiry
date of a CPPO offer
"""

import datetime
import json
import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# constants for the API
offer_id = "offer-1111111111111"

# days in the future
days_in_future = 30

future_date = datetime.date.today() + datetime.timedelta(days=days_in_future)

future_date_str = future_date.strftime("%Y-%m-%d")

details_object = {"AvailabilityEndDate": future_date_str}

details_string = json.dumps(details_object)

# main function to perform the action


def update_expiry_date_for_CPPO(mp_client):
    """
    update expiry date
    """
    try:
        response = mp_client.start_change_set(
            Catalog="AWSMarketplace",
            ChangeSet=[
                {
                    "ChangeType": "UpdateAvailability",
                    "Entity": {"Type": "Offer@1.0", "Identifier": offer_id},
                    "Details": details_string,
                }
            ],
            ChangeSetName="UpdateExpiryDate",
        )
        logger.info("Changeset created!")
        logger.info(f"ChangeSet ID: {response['ChangeSetId']}")
        logger.info(f"ChangeSet ARN: {response['ChangeSetArn']}")

    except ClientError as e:
        logger.exception(f"Couldn't update offer. {e}")
        raise


def usage_demo():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    print("-" * 88)
    print("Welcome to the update expiry date for CPPO offer")
    print("-" * 88)

    mp_client = boto3.client("marketplace-catalog")

    update_expiry_date_for_CPPO(mp_client)

    print("-" * 88)


if __name__ == "__main__":
    usage_demo()
