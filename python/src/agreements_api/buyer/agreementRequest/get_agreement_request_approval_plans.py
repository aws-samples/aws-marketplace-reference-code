# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import boto3


class GetAgreementRequestApprovalPlans:

    AGREEMENT_REQUEST_ID = "<AGREEMENT REQUEST ID HERE>"

    @staticmethod
    def get_agreement_request_approval_plans():
        client = boto3.client("marketplace-agreement")

        paginator = client.get_paginator("get_agreement_request_approval_plans")
        for page in paginator.paginate(agreementRequestId=GetAgreementRequestApprovalPlans.AGREEMENT_REQUEST_ID):
            for item in page["items"]:
                plan = item["buyerAgreementApprovalPlan"]
                print("Plan Reference: " + plan["planReference"])
                print("Plan Name: " + str(plan.get("name", "")))
                for level in plan["levels"]:
                    print("  Level: " + str(level.get("name", "")))
                    for group in level["groups"]:
                        print("    Required Approvals: " + str(group["approvalCriteria"]["requiredApprovalCount"]))
                        for approver in group["approvers"]:
                            print("    Approver: " + str(approver))
                print("---")


if __name__ == "__main__":
    GetAgreementRequestApprovalPlans.get_agreement_request_approval_plans()
