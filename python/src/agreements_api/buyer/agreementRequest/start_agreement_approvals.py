# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import boto3


class StartAgreementApprovals:

    AGREEMENT_REQUEST_ID = "<AGREEMENT REQUEST ID HERE>"
    # planReference of a plan returned by GetAgreementRequestApprovalPlans for this agreement request.
    PLAN_REFERENCE = "<PLAN REFERENCE HERE>"
    REQUESTER_NOTE = "<NOTE FOR THE APPROVERS HERE>"
    # Optional: a purchase order for an expected charge, by its id from GetAgreementRequest chargeSummary.
    CHARGE_ID = None
    PURCHASE_ORDER_REFERENCE = "<PURCHASE ORDER REFERENCE HERE>"

    @staticmethod
    def start_agreement_approvals():
        client = boto3.client("marketplace-agreement")

        kwargs = {
            "agreementRequestId": StartAgreementApprovals.AGREEMENT_REQUEST_ID,
            "planInputs": [
                {
                    "buyerAgreementApprovalPlanInput": {
                        "planReference": StartAgreementApprovals.PLAN_REFERENCE,
                        "requesterNote": StartAgreementApprovals.REQUESTER_NOTE,
                    }
                }
            ],
        }
        if StartAgreementApprovals.CHARGE_ID:
            kwargs["purchaseOrders"] = [
                {
                    "chargeId": StartAgreementApprovals.CHARGE_ID,
                    "purchaseOrderReference": StartAgreementApprovals.PURCHASE_ORDER_REFERENCE,
                }
            ]

        response = client.start_agreement_approvals(**kwargs)

        for summary in response["approvalSummaries"]:
            print("Approval Type: " + summary["approvalType"])
            print("Agreement Request ID: " + summary["agreementRequestId"])
            print("Agreement Approval ID: " + summary["agreementApprovalId"])
            print("Name: " + summary["name"])
            print("Status: " + summary["status"])
            print("Created At: " + str(summary["createdAt"]))
            print("Updated At: " + str(summary["updatedAt"]))
            print("Started At: " + str(summary.get("startedAt", "")))
            print("Expires At: " + str(summary.get("expiresAt", "")))
            print("Approval Needed By: " + str(summary["approvalNeededBy"]))
            print("---")


if __name__ == "__main__":
    StartAgreementApprovals.start_agreement_approvals()
