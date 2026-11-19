# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import boto3


# Rejects an agreement approval as the administrator of the buyer's AWS Organization. The agreement request
# is rejected and no agreement is created.
class RejectAgreementApproval:

    AGREEMENT_APPROVAL_ID = "<AGREEMENT APPROVAL ID HERE>"
    NOTE = "<REJECTION REASON HERE>"

    @staticmethod
    def reject_agreement_approval():
        client = boto3.client("marketplace-agreement")

        rejection_input = {
            "agreementApprovalId": RejectAgreementApproval.AGREEMENT_APPROVAL_ID,
            "note": RejectAgreementApproval.NOTE,
        }

        client.reject_agreement_approval(buyerAgreementApprovalRejectionInput=rejection_input)

        print("Rejected Agreement Approval ID: " + RejectAgreementApproval.AGREEMENT_APPROVAL_ID)


if __name__ == "__main__":
    RejectAgreementApproval.reject_agreement_approval()
