# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import boto3


class GetAgreementRequest:

    AGREEMENT_REQUEST_ID = "<AGREEMENT REQUEST ID HERE>"

    @staticmethod
    def get_agreement_request():
        client = boto3.client("marketplace-agreement")

        response = client.get_agreement_request(
            agreementRequestId=GetAgreementRequest.AGREEMENT_REQUEST_ID,
        )

        print("Agreement Request ID: " + response["agreementRequestId"])
        print("Agreement Type: " + str(response.get("agreementType", "")))
        print("Status: " + str(response.get("status", "")))
        print("Approval Requirement: " + str(response.get("approvalRequirement", "")))
        if "agreementId" in response:
            print("Agreement ID: " + response["agreementId"])
        print("Intent: " + str(response.get("intent", "")))
        print("Created At: " + str(response.get("createdAt", "")))

        charge_summary = response["chargeSummary"]
        print("Currency Code: " + str(charge_summary.get("currencyCode", "")))
        print("New Agreement Value: " + str(charge_summary.get("newAgreementValue", "")))
        # Tax fields are returned only when the request was created with tax estimation enabled.
        if "estimatedTaxes" in charge_summary:
            print("New Agreement Value After Tax: " + str(charge_summary.get("newAgreementValueAfterTax", "")))
            print("Estimated Taxes: " + str(charge_summary["estimatedTaxes"].get("totalAmount", "")))
            print("Invoicing Entity: " + str(charge_summary.get("invoicingEntity", "")))
        for charge in charge_summary.get("expectedCharges", []):
            print("Expected Charge ID: " + str(charge.get("id", "")))
            print("  Amount: " + str(charge.get("amount", "")))
            if "amountAfterTax" in charge:
                print("  Amount After Tax: " + charge["amountAfterTax"])
            print("  Timing: " + str(charge.get("timing", "")))
            # Recurring charges of usage-based and recurring payment terms have no time.
            if "time" in charge:
                print("  Time: " + str(charge["time"]))
            if "purchaseOrderReference" in charge:
                print("  Purchase Order Reference: " + charge["purchaseOrderReference"])
        for itemized_charge in charge_summary.get("itemizedCharges", []):
            print("Itemized Charge: " + str(itemized_charge.get("dimensionKey", "")) + ", quantity "
                  + str(itemized_charge.get("oldQuantity", "")) + " -> " + str(itemized_charge.get("newQuantity", ""))
                  + ", amount " + str(itemized_charge.get("incrementalChargeAmount", "")))

        print("Proposer Account ID: " + str(response["proposer"].get("accountId", "")))
        proposal_summary = response["proposalSummary"]
        print("Offer ID: " + str(proposal_summary.get("offerId", "")))
        if "offerSetId" in proposal_summary:
            print("Offer Set ID: " + proposal_summary["offerSetId"])
        for resource in proposal_summary.get("resources", []):
            print("Resource: " + resource["id"] + " (" + resource["type"] + ")")


if __name__ == "__main__":
    GetAgreementRequest.get_agreement_request()
