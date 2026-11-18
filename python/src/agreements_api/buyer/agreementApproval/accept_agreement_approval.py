# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import boto3


# Approves an agreement approval as the administrator of the buyer's AWS Organization. When the approval
# is approved, the agreement request is accepted and the agreement is created; GetAgreementRequest returns its
# agreementId.
class AcceptAgreementApproval:

    AGREEMENT_APPROVAL_ID = "<AGREEMENT APPROVAL ID HERE>"
    NOTE = "<APPROVAL NOTE HERE>"

    @staticmethod
    def accept_agreement_approval():
        client = boto3.client("marketplace-agreement")

        approver_input = {
            "agreementApprovalId": AcceptAgreementApproval.AGREEMENT_APPROVAL_ID,
            "note": AcceptAgreementApproval.NOTE,
        }

        client.accept_agreement_approval(buyerAgreementApprovalApproverInput=approver_input)

        print("Approved Agreement Approval ID: " + AcceptAgreementApproval.AGREEMENT_APPROVAL_ID)


if __name__ == "__main__":
    AcceptAgreementApproval.accept_agreement_approval()
