# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Purpose
Obtain what will happen to the agreement when it reaches its end date, and the reason for that outcome
AG-32
"""

import logging

import boto3
from botocore.exceptions import ClientError

mp_client = boto3.client("marketplace-agreement")

logger = logging.getLogger(__name__)

# agreement id
AGREEMENT_ID = "agmt-11111111111111111111"

# attribute names
ATTRIBUTE_END_TIME_BEHAVIOR = "endTimeBehavior"
ATTRIBUTE_TYPE = "type"
ATTRIBUTE_REASON_CODE = "reasonCode"
ATTRIBUTE_RENEWAL_SUMMARY = "renewalSummary"
ATTRIBUTE_OFFER_ID = "offerId"


def get_end_time_behavior(entity_id):
    """
    Returns the end time behavior of a given agreement
    Args: entity_id str: Agreement to describe
    Returns: dict: The endTimeBehavior of the agreement, or None if it has no end date
    """

    try:
        agreement = mp_client.describe_agreement(agreementId=entity_id)

        # endTimeBehavior is absent for agreements that have no end date, because those
        # agreements never reach an end time. Pay-as-you-go agreements are the most
        # common example.
        return agreement.get(ATTRIBUTE_END_TIME_BEHAVIOR)

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logger.error("Agreement with ID %s not found.", entity_id)
        else:
            logger.error("Unexpected error: %s", e)


def usage_demo():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    print("-" * 88)
    print("Looking for an agreement in the AWS Marketplace.")
    print("-" * 88)

    end_time_behavior = get_end_time_behavior(AGREEMENT_ID)

    if end_time_behavior is None:
        print(
            "Agreement "
            + AGREEMENT_ID
            + " was not found, or it has no end date and therefore no end time behavior."
        )
        return

    print(f"End time behavior is {end_time_behavior[ATTRIBUTE_TYPE]}")

    # reasonCode is only populated when type is EXPIRE or REPLACE. It is absent when type is RENEW.
    if ATTRIBUTE_REASON_CODE in end_time_behavior:
        print(f"Reason is {end_time_behavior[ATTRIBUTE_REASON_CODE]}")

    # renewalSummary carries the offer that the next renewal will use. It is present whenever
    # type is RENEW, but offerId inside it is absent until a renewal offer is created.
    offer_id = end_time_behavior.get(ATTRIBUTE_RENEWAL_SUMMARY, {}).get(ATTRIBUTE_OFFER_ID)
    if offer_id:
        print(f"Next renewal will use offer {offer_id}")


if __name__ == "__main__":
    usage_demo()
