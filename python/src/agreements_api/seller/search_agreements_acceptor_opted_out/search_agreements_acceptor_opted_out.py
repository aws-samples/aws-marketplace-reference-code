# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Purpose
Shows how to use the AWS SDK for Python (Boto3) to search for the agreements the acceptor opted out
of renewing
AG-36

This filter is supported only when PartyType is Proposer, so only sellers can use it. An
unsupported combination fails with a ValidationException whose reason is UNSUPPORTED_FILTERS.
All filter combinations we support for Proposer and Acceptor:
https://docs.aws.amazon.com/marketplace/latest/APIReference/API_marketplace-agreements_SearchAgreements.html
"""

import logging

import boto3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import utils.helpers as helper
from botocore.exceptions import ClientError

mp_client = boto3.client("marketplace-agreement")

# change to 'PROPOSER_RENEW_OPTED_OUT', 'NO_RENEWAL_TERM', or 'RENEWAL_LIMIT_EXHAUSTED' for the
# other reasons an agreement does not renew
endTimeBehaviorReasonCodeFilterValue = "ACCEPTOR_RENEW_OPTED_OUT"

MAX_PAGE_RESULTS = 10

logger = logging.getLogger(__name__)


def get_agreements():
    AgreementSummaryList = []

    try:
        agreement = mp_client.search_agreements(
            catalog="AWSMarketplace",
            maxResults=MAX_PAGE_RESULTS,
            # This filter is supported only for the proposer, so leave PartyType set to
            # "Proposer". "Acceptor" fails with a ValidationException whose reason is
            # UNSUPPORTED_FILTERS.
            filters=[
                {"name": "PartyType", "values": ["Proposer"]},
                {
                    "name": "EndTimeBehaviorReasonCode",
                    "values": [endTimeBehaviorReasonCodeFilterValue],
                },
                {"name": "AgreementType", "values": ["PurchaseAgreement"]},
            ],
        )
    except ClientError as e:
        logger.error("Could not complete search_agreements request.")
        raise

    AgreementSummaryList.extend(agreement["agreementViewSummaries"])

    while "nextToken" in agreement:
        try:
            agreement = mp_client.search_agreements(
                catalog="AWSMarketplace",
                maxResults=MAX_PAGE_RESULTS,
                nextToken=agreement["nextToken"],
                filters=[
                    {"name": "PartyType", "values": ["Proposer"]},
                    {
                        "name": "EndTimeBehaviorReasonCode",
                        "values": [endTimeBehaviorReasonCodeFilterValue],
                    },
                    {"name": "AgreementType", "values": ["PurchaseAgreement"]},
                ],
            )
        except ClientError as e:
            logger.error("Could not complete search_agreements request.")
            raise

        AgreementSummaryList.extend(agreement["agreementViewSummaries"])

    return AgreementSummaryList


if __name__ == "__main__":
    agreements = get_agreements()
    helper.pretty_print_datetime(agreements)
