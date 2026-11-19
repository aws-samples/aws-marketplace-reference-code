# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import boto3


class GetAgreementApproval:

    AGREEMENT_APPROVAL_ID = "<AGREEMENT APPROVAL ID HERE>"

    @staticmethod
    def get_agreement_approval():
        client = boto3.client("marketplace-agreement")

        response = client.get_agreement_approval(
            agreementApprovalId=GetAgreementApproval.AGREEMENT_APPROVAL_ID,
        )
        approval = response["buyerAgreementApproval"]

        print("Approval Type: " + approval["approvalType"])
        print("Agreement Approval ID: " + approval["agreementApprovalId"])
        print("Agreement Request ID: " + approval["agreementRequestId"])
        print("Name: " + approval["name"])
        print("Status: " + approval["status"])
        print("Requester Account ID: " + approval["requester"]["accountId"])
        print("Proposer: " + approval["proposer"]["legalName"] + " (" + approval["proposer"]["accountId"] + ")")
        proposal_summary = approval["proposalSummary"]
        print("Offer ID: " + proposal_summary["offerId"])
        if "offerSetId" in proposal_summary:
            print("Offer Set ID: " + proposal_summary["offerSetId"])
        print("Visibility Scope: " + proposal_summary["visibilityScope"])
        for resource in proposal_summary.get("resources", []):
            print("Resource: " + resource["name"] + " (" + resource["id"] + ", " + resource["type"] + ")")
        print("Plan Reference: " + approval["planInput"]["planReference"])
        if "requesterNote" in approval["planInput"]:
            print("Requester Note: " + approval["planInput"]["requesterNote"])
        print("Created At: " + str(approval["createdAt"]))
        print("Updated At: " + str(approval["updatedAt"]))
        print("Started At: " + str(approval.get("startedAt", "")))
        print("Expires At: " + str(approval.get("expiresAt", "")))
        print("Approval Needed By: " + str(approval["approvalNeededBy"]))
        for level in approval["levels"]:
            print("  Level: " + str(level.get("name", "")))
            for group in level["groups"]:
                print("    Required Approvals: " + str(group["approvalCriteria"]["requiredApprovalCount"]))
                for outcome in group["approvers"]:
                    GetAgreementApproval.print_approver_outcome(outcome)

    @staticmethod
    def print_approver_outcome(outcome):
        if "awsOrganizationApproverOutcome" in outcome:
            admin = outcome["awsOrganizationApproverOutcome"]
            print("    Organization admin: " + admin["status"]
                  + ", approverOutcomeId " + str(admin.get("approverOutcomeId", "")))
        elif "emailApproverOutcome" in outcome:
            email = outcome["emailApproverOutcome"]
            print("    Email approver " + email["emailAddress"] + ": " + email["status"]
                  + ", approverOutcomeId " + str(email.get("approverOutcomeId", "")))
        elif "procurementToolApproverOutcome" in outcome:
            tool = outcome["procurementToolApproverOutcome"]
            print("    Procurement tool " + str(tool.get("name", "")) + ": " + tool["status"]
                  + ", approverOutcomeId " + str(tool.get("approverOutcomeId", "")))
        else:
            print("    Approver: " + str(outcome))


if __name__ == "__main__":
    GetAgreementApproval.get_agreement_approval()
