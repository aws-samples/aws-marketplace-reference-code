# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Purpose
Obtain the auto-renewal status of the agreement
AG-15
"""

import json
import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

import utils.helpers as helper


import boto3
from botocore.exceptions import ClientError

mp_client = boto3.client("marketplace-agreement")

logger = logging.getLogger(__name__)

# agreement id
AGREEMENT_ID = "agmt-11111111111111111111"

# to use sample file or not
USE_SAMPLE_FILE = False
SAMPLE_FILE_NAME = "mockup_agreement_terms.json"

# attribute name
ROOT_ELEM = "acceptedTerms"
TERM_NAME = "renewalTerm"
CONFIG_ELEM = "configuration"
ATTRIBUTE_NAME = "enableAutoRenew"


def get_renewal_term(entity_id):
    """
    Reads the agreement's renewal term. These values come from the offer and are read-only here.
    Args: entity_id str: Agreement to read the terms of
    Returns: dict: The first renewal term found, or None when the agreement has none
    """

    try:
        next_token = None

        while True:
            if USE_SAMPLE_FILE:
                sample_file = os.path.join(os.path.dirname(__file__), SAMPLE_FILE_NAME)
                terms = open_json_file(sample_file)
            elif next_token is None:
                terms = mp_client.get_agreement_terms(agreementId=entity_id)
            else:
                terms = mp_client.get_agreement_terms(
                    agreementId=entity_id, nextToken=next_token
                )

            for term in terms[ROOT_ELEM]:
                # acceptedTerms is a union. Only the renewal term is of interest here.
                if TERM_NAME in term:
                    return term[TERM_NAME]

            if USE_SAMPLE_FILE:
                break

            next_token = terms.get("nextToken")
            if not next_token:
                break

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logger.error("Agreement with ID %s not found.", entity_id)
        else:
            logger.error("Unexpected error: %s", e)

    return None


def get_auto_renewal(entity_id):
    """
    Returns whether the agreement is set to auto renew, or "No Auto Renewal" when there is no
    renewal term or the flag is not set. Delegates to get_renewal_term so there is a single API path.
    Args: entity_id str: Agreement to read the terms of
    Returns: str: "True"/"False", or "No Auto Renewal"
    """

    renewal_term = get_renewal_term(entity_id)

    if (
        renewal_term is not None
        and CONFIG_ELEM in renewal_term
        and renewal_term[CONFIG_ELEM].get(ATTRIBUTE_NAME) is not None
    ):
        return str(renewal_term[CONFIG_ELEM].get(ATTRIBUTE_NAME))
    return "No Auto Renewal"


def print_renewal_term(renewal_term):
    """
    Prints the fields of a renewal term.
    Args: renewal_term dict: A renewal term, or None
    """

    if renewal_term is None:
        print("No Auto Renewal")
        return

    print("Renewal Term ID: " + str(renewal_term.get("id")))

    if CONFIG_ELEM in renewal_term:
        print(
            "Auto Renew Enabled: "
            + str(renewal_term[CONFIG_ELEM].get(ATTRIBUTE_NAME))
        )

    # ISO 8601 duration. The customer can no longer change enableAutoRenew once the
    # agreement is within this duration of its end date. Absent when the offer sets no deadline,
    # which leaves the customer free to change enableAutoRenew up to the end date.
    if "lockoutPeriod" in renewal_term:
        print("Lockout Period: " + str(renewal_term["lockoutPeriod"]))
    else:
        print("Lockout Period: none")

    # Absent means the agreement can renew without limit.
    if "maxRenewals" in renewal_term:
        print("Max Renewals: " + str(renewal_term["maxRenewals"]))
    else:
        print("Max Renewals: unlimited")

    # Absent unless the offer sets a separate deadline for adjusting the renewal price.
    if "adjustmentDeadline" in renewal_term:
        print("Adjustment Deadline: " + str(renewal_term["adjustmentDeadline"]))

    print_price_increase(renewal_term.get("priceIncrease"))

    for term_template in renewal_term.get("termTemplates", []):
        print_term_template(term_template)


def print_price_increase(price_increase):
    """
    Prints the price change that applies when the agreement renews.
    Args: price_increase dict: The priceIncrease union from the renewal term
    """

    if price_increase is None:
        print("Price Increase: none (the price does not change at renewal)")
        return

    # priceIncrease is a union. Exactly one variant is set.
    if "fixedPercentage" in price_increase:
        print(
            "Fixed Price Increase Percentage: "
            + str(price_increase["fixedPercentage"].get("value"))
        )
    elif "percentageRange" in price_increase:
        # The uplift is open within this range; defaultValue applies if you take no action.
        percentage_range = price_increase["percentageRange"]
        print("Price Increase Min Percentage: " + str(percentage_range.get("minValue")))
        print("Price Increase Max Percentage: " + str(percentage_range.get("maxValue")))
        print(
            "Price Increase Default Percentage: "
            + str(percentage_range.get("defaultValue"))
        )


def print_term_template(term_template):
    """
    Prints the term template that applies when the agreement renews.
    Args: term_template dict: A termTemplates entry from the renewal term
    """

    # termTemplates entries are a union. Only payment schedule templates are supported today.
    if "paymentScheduleTermTemplate" not in term_template:
        print("Term Template: not a payment schedule template")
        return

    print("Payment Schedule Template:")
    for entry in term_template["paymentScheduleTermTemplate"].get("schedule", []):
        # chargeDateOffset is relative to the start of the renewed agreement, e.g. "P3M".
        line = (
            "  Charge Date Offset: "
            + str(entry.get("chargeDateOffset"))
            + ", Charge Percentage: "
            + str(entry.get("chargePercentage"))
        )

        # Absent unless the schedule pins charges to a day of the month.
        if "dayOfMonth" in entry:
            line += ", Day Of Month: " + str(entry["dayOfMonth"])

        print(line)


def print_end_time_behavior(entity_id):
    """
    Prints the agreement's end time behavior: whether it will renew, be replaced, or expire, and why.
    Args: entity_id str: Agreement to describe
    """

    try:
        agreement = mp_client.describe_agreement(agreementId=entity_id)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logger.error("Agreement with ID %s not found.", entity_id)
        else:
            logger.error("Unexpected error: %s", e)
        return

    end_time_behavior = agreement.get("endTimeBehavior")
    if end_time_behavior is None:
        print("End Time Behavior: none (this agreement has no end date)")
        return

    print("End Time Behavior Type: " + str(end_time_behavior.get("type")))

    # The reason the agreement does not renew, and absent when it does. My own PROPOSER_RENEW_OPTED_OUT
    # leaves enableAutoRenew untouched, so the flag can read True even when this says it will not renew.
    if "reasonCode" in end_time_behavior:
        print("End Time Behavior Reason Code: " + str(end_time_behavior["reasonCode"]))

    # renewalSummary is present whenever type is RENEW, but offerId inside it is absent
    # until a renewal offer is created.
    offer_id = end_time_behavior.get("renewalSummary", {}).get("offerId")
    if offer_id:
        print("Renewal Offer ID: " + offer_id)


def usage_demo():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    print("-" * 88)
    print("Looking for an agreement in the AWS Marketplace.")
    print("-" * 88)

    print_renewal_term(get_renewal_term(AGREEMENT_ID))

    # USE_SAMPLE_FILE only mocks the GetAgreementTerms response. endTimeBehavior comes from
    # DescribeAgreement, which has no sample file, so skip it when running from the sample.
    if not USE_SAMPLE_FILE:
        print_end_time_behavior(AGREEMENT_ID)


# open json file from path
def open_json_file(filename):
    with open(filename, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    usage_demo()
