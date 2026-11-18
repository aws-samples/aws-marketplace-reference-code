# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import boto3


class ListAgreementRequests:

    STATUS = "PENDING_APPROVAL"

    @staticmethod
    def list_agreement_requests():
        client = boto3.client("marketplace-agreement")

        next_token = None

        while True:
            kwargs = {"status": ListAgreementRequests.STATUS}
            if next_token:
                kwargs["nextToken"] = next_token

            response = client.list_agreement_requests(**kwargs)

            for summary in response.get("items", []):
                print("Agreement Request ID: " + summary["agreementRequestId"])
                print("Agreement Type: " + str(summary.get("agreementType", "")))
                print("Status: " + str(summary.get("status", "")))
                if "agreementId" in summary:
                    print("Agreement ID: " + summary["agreementId"])
                proposal_summary = summary["proposalSummary"]
                print("Offer ID: " + str(proposal_summary.get("offerId", "")))
                if "offerSetId" in proposal_summary:
                    print("Offer Set ID: " + proposal_summary["offerSetId"])
                for resource in proposal_summary.get("resources", []):
                    print("Resource: " + resource["id"] + " (" + resource["type"] + ")")
                print("---")

            next_token = response.get("nextToken")
            if not next_token:
                break


if __name__ == "__main__":
    ListAgreementRequests.list_agreement_requests()
