import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import boto3


class AcceptAgreementCancellationRequest:

    AGREEMENT_ID = "<AGREEMENT ID HERE>"
    AGREEMENT_CANCELLATION_REQUEST_ID = "<AGREEMENT CANCELLATION REQUEST ID HERE>"

    @staticmethod
    def accept_agreement_cancellation_request():
        client = boto3.client("marketplace-agreement")

        response = client.accept_agreement_cancellation_request(
            agreementId=AcceptAgreementCancellationRequest.AGREEMENT_ID,
            agreementCancellationRequestId=AcceptAgreementCancellationRequest.AGREEMENT_CANCELLATION_REQUEST_ID,
        )

        print("Agreement ID: " + response["agreementId"])
        print("Cancellation Request ID: " + response["agreementCancellationRequestId"])
        print("Status: " + str(response.get("status", "")))
        print("Description: " + str(response.get("description", "")))
        print("Reason Code: " + str(response.get("reasonCode", "")))
        print("Created At: " + str(response.get("createdAt", "")))
        print("Updated At: " + str(response.get("updatedAt", "")))


if __name__ == "__main__":
    AcceptAgreementCancellationRequest.accept_agreement_cancellation_request()
