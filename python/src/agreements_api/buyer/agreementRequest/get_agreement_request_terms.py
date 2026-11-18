# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import boto3

import json


class GetAgreementRequestTerms:

    AGREEMENT_REQUEST_ID = "<AGREEMENT REQUEST ID HERE>"

    @staticmethod
    def get_agreement_request_terms():
        client = boto3.client("marketplace-agreement")

        paginator = client.get_paginator("get_agreement_request_terms")
        for page in paginator.paginate(agreementRequestId=GetAgreementRequestTerms.AGREEMENT_REQUEST_ID):
            for term in page["terms"]:
                term_type, term_value = next(iter(term.items()))
                print("Term Type: " + term_type)
                print(json.dumps(term_value, indent=2, default=str))
                print("---")


if __name__ == "__main__":
    GetAgreementRequestTerms.get_agreement_request_terms()
