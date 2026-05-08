# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Demonstrates how to create a SaaS agreement with CONTRACT pricing model with upfront payment
using the AWS Marketplace Agreement Service APIs.

Scenario: A buyer subscribes to a SaaS product using a ConfigurableUpfrontPricingTerm,
selecting an agreement duration and specifying quantities for multiple dimensions.
Tax estimation is enabled at the time of agreement creation.

Before running this sample, replace the placeholder constants below with values from
your AWS Marketplace offer:
  - AGREEMENT_PROPOSAL_IDENTIFIER — the agreementProposalId from the offer.
  - Term IDs (starting with term-) — found in the offer's term list.
  - SELECTOR_VALUE — duration for the agreement (e.g., P12M for 12 months).
  - DIMENSION_1_KEY, DIMENSION_2_KEY — dimension keys defined in the offer.
  - DIMENSION_1_VALUE, DIMENSION_2_VALUE — quantities for each dimension.
"""

import boto3

from utils.agreement_api_utils import generate_client_token


class NewSaaSContractWithUpfrontPayment:

    # The agreementProposalId from the offer.
    AGREEMENT_PROPOSAL_IDENTIFIER = "<your-agreement-proposal-identifier>"

    # Term ID for the ConfigurableUpfrontPricingTerm in your offer.
    CONFIGURABLE_UPFRONT_PRICING_TERM_ID = "<your-configurable-upfront-pricing-term-id>"

    # Duration for the agreement (e.g., "P12M" for 12 months).
    SELECTOR_VALUE = "<your-selector-value>"

    # First dimension key and quantity defined in your offer.
    DIMENSION_1_KEY = "<your-dimension-1-key>"
    DIMENSION_1_VALUE = 10

    # Second dimension key and quantity defined in your offer.
    DIMENSION_2_KEY = "<your-dimension-2-key>"
    DIMENSION_2_VALUE = 20

    # Term ID for the LegalTerm in your offer.
    LEGAL_TERM_ID = "<your-legal-term-id>"

    # Tax estimation setting: "ENABLED" to include estimated taxes in the agreement.
    TAX_ESTIMATION = "ENABLED"

    @staticmethod
    def create_saas_contract_agreement():
        """
        Create a SaaS agreement with CONTRACT pricing model with configurable upfront pricing
        for multiple dimensions and tax estimation.
        """
        client = boto3.client("marketplace-agreement")

        configurable_upfront_pricing_term = {
            "id": NewSaaSContractWithUpfrontPayment.CONFIGURABLE_UPFRONT_PRICING_TERM_ID,
            "configuration": {
                "configurableUpfrontPricingTermConfiguration": {
                    "selectorValue": NewSaaSContractWithUpfrontPayment.SELECTOR_VALUE,
                    "dimensions": [
                        {
                            "dimensionKey": NewSaaSContractWithUpfrontPayment.DIMENSION_1_KEY,
                            "dimensionValue": NewSaaSContractWithUpfrontPayment.DIMENSION_1_VALUE,
                        },
                        {
                            "dimensionKey": NewSaaSContractWithUpfrontPayment.DIMENSION_2_KEY,
                            "dimensionValue": NewSaaSContractWithUpfrontPayment.DIMENSION_2_VALUE,
                        },
                    ],
                }
            },
        }

        legal_term = {"id": NewSaaSContractWithUpfrontPayment.LEGAL_TERM_ID}

        create_response = client.create_agreement_request(
            clientToken=generate_client_token(),
            intent="NEW",
            requestedTerms=[configurable_upfront_pricing_term, legal_term],
            taxConfiguration={"taxEstimation": NewSaaSContractWithUpfrontPayment.TAX_ESTIMATION},
            agreementProposalIdentifier=NewSaaSContractWithUpfrontPayment.AGREEMENT_PROPOSAL_IDENTIFIER,
        )
        agreement_request_id = create_response["agreementRequestId"]
        print("Agreement request created. AgreementRequestId: " + agreement_request_id)

        accept_response = client.accept_agreement_request(
            agreementRequestId=agreement_request_id
        )
        print(
            "SaaS agreement request with CONTRACT pricing model accepted. AgreementId: "
            + accept_response["agreementId"]
        )


if __name__ == "__main__":
    NewSaaSContractWithUpfrontPayment.create_saas_contract_agreement()
