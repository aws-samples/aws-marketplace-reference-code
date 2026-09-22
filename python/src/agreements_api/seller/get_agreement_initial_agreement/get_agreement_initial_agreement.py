# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Purpose
Obtain the first agreement in this agreement's chain
AG-33
"""

import logging

import boto3
from botocore.exceptions import ClientError

mp_client = boto3.client("marketplace-agreement")

logger = logging.getLogger(__name__)

# agreement id
AGREEMENT_ID = "agmt-11111111111111111111"

# attribute name
ATTRIBUTE_INITIAL_AGREEMENT_ID = "initialAgreementId"


def get_initial_agreement_id(entity_id):
    """
    Returns the first agreement in the chain that the given agreement belongs to
    Args: entity_id str: Agreement to describe
    Returns: str: The initial agreement id. Equals entity_id when this agreement starts the chain.
    """

    try:
        agreement = mp_client.describe_agreement(agreementId=entity_id)
        return agreement.get(ATTRIBUTE_INITIAL_AGREEMENT_ID)

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

    # A renewal or replacement carries forward the same initialAgreementId, so this value
    # identifies the whole chain. It equals AGREEMENT_ID when this agreement starts the chain.
    print("Initial Agreement ID: " + str(get_initial_agreement_id(AGREEMENT_ID)))


if __name__ == "__main__":
    usage_demo()
