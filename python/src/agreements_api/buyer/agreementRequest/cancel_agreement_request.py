# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import boto3


# Cancels an agreement request that is pending approval, and its approval.
class CancelAgreementRequest:

    AGREEMENT_REQUEST_ID = "<AGREEMENT REQUEST ID HERE>"

    @staticmethod
    def cancel_agreement_request():
        client = boto3.client("marketplace-agreement")

        client.cancel_agreement_request(
            agreementRequestId=CancelAgreementRequest.AGREEMENT_REQUEST_ID,
        )

        print("Cancelled Agreement Request ID: " + CancelAgreementRequest.AGREEMENT_REQUEST_ID)


if __name__ == "__main__":
    CancelAgreementRequest.cancel_agreement_request()
