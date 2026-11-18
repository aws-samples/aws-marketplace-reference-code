# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import boto3


class ListAgreementApprovals:

    # REQUESTER lists the approvals the caller started. AWS_ORGANIZATION_ADMIN lists the approvals the caller
    # decides as the administrator of its AWS Organization.
    PARTY_TYPE = "AWS_ORGANIZATION_ADMIN"
    STATUS = "PENDING_APPROVAL"

    @staticmethod
    def list_agreement_approvals():
        client = boto3.client("marketplace-agreement")

        next_token = None

        while True:
            kwargs = {"partyType": ListAgreementApprovals.PARTY_TYPE, "status": ListAgreementApprovals.STATUS}
            if next_token:
                kwargs["nextToken"] = next_token

            response = client.list_agreement_approvals(**kwargs)

            for summary in response["items"]:
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

            next_token = response.get("nextToken")
            if not next_token:
                break


if __name__ == "__main__":
    ListAgreementApprovals.list_agreement_approvals()
