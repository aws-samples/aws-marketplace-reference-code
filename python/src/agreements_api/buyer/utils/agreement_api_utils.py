# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""Utility functions for AWS Marketplace Agreement Service API samples."""

import json
import time
import uuid

def format_output(result):
    """Pretty-print an API response as JSON."""
    print(json.dumps(result, indent=2, default=str))


def generate_client_token():
    """Generate a unique client token for idempotent requests."""
    return str(uuid.uuid4())


def poll_until_entitlements_available(client, agreement_id):
    """Poll GetAgreementEntitlements until none are PENDING (up to 15 min)."""
    timeout = 15 * 60
    backoff = 2
    max_backoff = 60
    deadline = time.monotonic() + timeout

    while True:
        response = client.get_agreement_entitlements(agreementId=agreement_id)
        all_active = all(
            e.get("status") != "PENDING"
            for e in response.get("agreementEntitlements", [])
        )
        if all_active:
            return response
        if time.monotonic() + backoff > deadline:
            raise RuntimeError(
                f"Entitlements still pending after 15 minutes for agreementId: {agreement_id}"
            )
        print(f"Entitlements not yet active. Retrying in {backoff} seconds...")
        time.sleep(backoff)
        backoff = min(backoff * 2, max_backoff)


def print_renewal_term(client, agreement_id):
    """Print the renewal term that the proposer set on the offer."""
    next_token = None

    while True:
        request = {"agreementId": agreement_id}
        if next_token:
            request["nextToken"] = next_token

        response = client.get_agreement_terms(**request)

        for accepted_term in response.get("acceptedTerms", []):
            renewal_term = accepted_term.get("renewalTerm")
            if not renewal_term:
                continue

            print("Renewal Term ID: " + str(renewal_term.get("id", "")))

            configuration = renewal_term.get("configuration")
            if configuration:
                print("Auto Renew Enabled: " + str(configuration.get("enableAutoRenew", "")))

            lockout_period = renewal_term.get("lockoutPeriod")
            if lockout_period:
                print("Lockout Period: " + lockout_period)

            max_renewals = renewal_term.get("maxRenewals")
            if max_renewals is not None:
                print("Max Renewals: " + str(max_renewals))

            adjustment_deadline = renewal_term.get("adjustmentDeadline")
            if adjustment_deadline:
                print("Adjustment Deadline: " + adjustment_deadline)

            print_price_increase(renewal_term.get("priceIncrease"))

            for term_template in renewal_term.get("termTemplates", []):
                print_term_template(term_template)

        next_token = response.get("nextToken")
        if not next_token:
            break


def print_price_increase(price_increase):
    """Print the price increase that is applied each time the agreement renews."""
    if not price_increase:
        print("Price Increase: none (no uplift is set, so the agreement renews at the same price)")
        return

    fixed_percentage = price_increase.get("fixedPercentage")
    percentage_range = price_increase.get("percentageRange")

    if fixed_percentage:
        value = str(fixed_percentage.get("value", ""))
        if float(value) == 0:
            print("Fixed Price Increase Percentage: " + value
                  + " (the agreement renews at the same price)")
        else:
            print("Fixed Price Increase Percentage: " + value)
    elif percentage_range:
        print("Price Increase Min Percentage: " + str(percentage_range.get("minValue", "")))
        print("Price Increase Max Percentage: " + str(percentage_range.get("maxValue", "")))
        print("Price Increase Default Percentage: " + str(percentage_range.get("defaultValue", "")))


def print_term_template(term_template):
    """termTemplate is a union. Payment schedules are the only variant the renewal term
    supports today, so any other variant is skipped rather than printed."""
    payment_schedule_term_template = term_template.get("paymentScheduleTermTemplate")
    if not payment_schedule_term_template:
        return

    print("Payment Schedule Template:")
    for entry in payment_schedule_term_template.get("schedule", []):
        line = ("  Charge Date Offset: " + str(entry.get("chargeDateOffset", ""))
                + ", Charge Percentage: " + str(entry.get("chargePercentage", "")))

        day_of_month = entry.get("dayOfMonth")
        if day_of_month is not None:
            line += ", Day Of Month: " + str(day_of_month)

        print(line)


def print_end_time_behavior(client, agreement_id, label):
    """Print the end time behavior of an agreement."""
    describe_response = client.describe_agreement(agreementId=agreement_id)

    end_time_behavior = describe_response.get("endTimeBehavior")
    if not end_time_behavior:
        print(label + " - End Time Behavior: none (this agreement has no end date)")
        return

    print(label + " - End Time Behavior Type: " + str(end_time_behavior.get("type", "")))

    reason_code = end_time_behavior.get("reasonCode")
    if reason_code:
        print(label + " - End Time Behavior Reason Code: " + reason_code)

    offer_id = end_time_behavior.get("renewalSummary", {}).get("offerId")
    if offer_id:
        print(label + " - Renewal Offer ID: " + offer_id)
