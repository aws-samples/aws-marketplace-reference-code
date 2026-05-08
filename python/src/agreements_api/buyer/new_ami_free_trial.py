# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Demonstrates how to create an AMI Free Trial agreement
using the AWS Marketplace Agreement Service APIs.

Scenario: A buyer subscribes to an AMI product that offers a free trial period.
The free trial includes a FreeTrialPricingTerm alongside a UsageBasedPricingTerm.

Before running this sample, replace the placeholder constants below with values from
your AWS Marketplace offer:
  - AGREEMENT_PROPOSAL_IDENTIFIER — the agreementProposalId from the offer.
  - Term IDs (starting with term-) — found in the offer's term list.
"""

import boto3

from utils.agreement_api_utils import generate_client_token


class NewAmiFreeTrial:

    # The agreementProposalId from the offer.
    AGREEMENT_PROPOSAL_IDENTIFIER = "<your-agreement-proposal-identifier>"

    # Term ID for the FreeTrialPricingTerm in your offer.
    FREE_TRIAL_PRICING_TERM_ID = "<your-free-trial-pricing-term-id>"

    # Term ID for the UsageBasedPricingTerm in your offer (applies after the trial ends).
    USAGE_BASED_PRICING_TERM_ID = "<your-usage-based-pricing-term-id>"

    # Term ID for the SupportTerm in your offer.
    SUPPORT_TERM_ID = "<your-support-term-id>"

    # Term ID for the LegalTerm in your offer.
    LEGAL_TERM_ID = "<your-legal-term-id>"

    @staticmethod
    def create_and_accept_ami_free_trial_agreement_request():
        """
        Create an AMI Free Trial agreement.

        The FreeTrialPricingTerm grants access at no cost for the trial period.
        The UsageBasedPricingTerm defines the charges that apply once the trial ends.
        """
        client = boto3.client("marketplace-agreement")

        create_response = client.create_agreement_request(
            clientToken=generate_client_token(),
            intent="NEW",
            requestedTerms=[
                {"id": NewAmiFreeTrial.FREE_TRIAL_PRICING_TERM_ID},
                {"id": NewAmiFreeTrial.USAGE_BASED_PRICING_TERM_ID},
                {"id": NewAmiFreeTrial.SUPPORT_TERM_ID},
                {"id": NewAmiFreeTrial.LEGAL_TERM_ID},
            ],
            agreementProposalIdentifier=NewAmiFreeTrial.AGREEMENT_PROPOSAL_IDENTIFIER,
        )
        agreement_request_id = create_response["agreementRequestId"]
        print("Agreement request created. AgreementRequestId: " + agreement_request_id)

        accept_response = client.accept_agreement_request(
            agreementRequestId=agreement_request_id
        )
        print(
            "Agreement request with freeTrialPricingTerm accepted. AgreementId: "
            + accept_response["agreementId"]
        )


if __name__ == "__main__":
    NewAmiFreeTrial.create_and_accept_ami_free_trial_agreement_request()
