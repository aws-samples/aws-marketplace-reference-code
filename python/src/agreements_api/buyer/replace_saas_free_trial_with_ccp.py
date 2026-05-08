"""
Demonstrates how to create a SaaS free trial agreement and then replace it with a
paid Contract with Consumption Pricing (CCP) offer using the AWS Marketplace Agreement Service APIs.

Scenario: A buyer first starts a free trial on a SaaS product. Once the trial is active,
they decide to convert by replacing it with a paid offer that includes a
FixedUpfrontPricingTerm, PaymentScheduleTerm, and UsageBasedPricingTerm.

Flow:
  1. Create a SaaS free trial agreement with freeTrialPricingTerm.
  2. Wait for freeTrialPricingTerm agreement entitlements to become active.
  3. Replace the free trial agreement with the paid CCP offer using Intent.REPLACE.

Before running this sample, replace the placeholder constants below with values from
your AWS Marketplace offers:
  - AGREEMENT_PROPOSAL_IDENTIFIER — the agreementProposalId from the free trial offer.
  - NEW_AGREEMENT_PROPOSAL_IDENTIFIER — the agreementProposalId from the paid CCP offer.
  - Term IDs (starting with term-) — found in each offer's term list.
"""

import boto3

from utils.agreement_api_utils import (
    format_output,
    generate_client_token,
    poll_until_entitlements_available,
)


class ReplaceSaaSFreeTrialWithCCP:

    # The agreementProposalId from the free trial offer.
    AGREEMENT_PROPOSAL_IDENTIFIER = "<your-free-trial-agreement-proposal-identifier>"

    # Term ID for the FreeTrialPricingTerm in the free trial offer.
    FREE_TRIAL_PRICING_TERM_ID = "<your-free-trial-pricing-term-id>"

    # Term ID for the LegalTerm in the free trial offer.
    LEGAL_TERM_ID = "<your-legal-term-id>"

    # The agreementProposalId from the paid CCP offer to convert to.
    NEW_AGREEMENT_PROPOSAL_IDENTIFIER = "<your-ccp-agreement-proposal-identifier>"

    # Term ID for the FixedUpfrontPricingTerm in the CCP offer.
    FIXED_UPFRONT_PRICING_TERM_ID = "<your-fixed-upfront-pricing-term-id>"

    # Term ID for the PaymentScheduleTerm in the CCP offer.
    PAYMENT_SCHEDULE_TERM_ID = "<your-payment-schedule-term-id>"

    # Term ID for the UsageBasedPricingTerm in the CCP offer.
    USAGE_BASED_PRICING_TERM_ID = "<your-usage-based-pricing-term-id>"

    # Term ID for the ValidityTerm in the CCP offer.
    VALIDITY_TERM_ID = "<your-validity-term-id>"

    # Term ID for the LegalTerm in the CCP offer.
    NEW_LEGAL_TERM_ID = "<your-new-legal-term-id>"

    @staticmethod
    def create_saas_free_trial_and_replace_with_ccp():
        """
        Full end-to-end flow:
        1. Create a SaaS free trial agreement with freeTrialPricingTerm.
        2. Wait for freeTrialPricingTerm agreement entitlements to become active.
        3. Replace the free trial agreement with the paid CCP offer.
        """
        client = boto3.client("marketplace-agreement")
        cls = ReplaceSaaSFreeTrialWithCCP

        legal_term = {"id": cls.LEGAL_TERM_ID}
        free_trial_pricing_term = {"id": cls.FREE_TRIAL_PRICING_TERM_ID}

        # --- Step 1: Agreement with freeTrialPricingTerm ---
        create_response = client.create_agreement_request(
            clientToken=generate_client_token(),
            intent="NEW",
            requestedTerms=[free_trial_pricing_term, legal_term],
            agreementProposalIdentifier=cls.AGREEMENT_PROPOSAL_IDENTIFIER,
        )
        agreement_request_id = create_response["agreementRequestId"]
        print("Agreement request with freeTrialPricingTerm created. AgreementRequestId: " + agreement_request_id)

        accept_response = client.accept_agreement_request(
            agreementRequestId=agreement_request_id
        )
        agreement_id = accept_response["agreementId"]
        print("Agreement request with freeTrialPricingTerm accepted. AgreementId: " + agreement_id)

        # Wait for freeTrialPricingTerm agreement entitlements to become active before replacing.
        print("Waiting for freeTrialPricingTerm agreement entitlements to become active...")
        entitlements_response = poll_until_entitlements_available(client, agreement_id)
        print("freeTrialPricingTerm agreement entitlements are now active.")
        format_output(entitlements_response)

        # --- Step 2: Replace Agreement with freeTrialPricingTerm with Paid CCP Offer ---
        # Use Intent.REPLACE and sourceAgreementIdentifier to replace the free trial agreement.
        usage_based_pricing_term = {"id": cls.USAGE_BASED_PRICING_TERM_ID}
        fixed_upfront_pricing_term = {"id": cls.FIXED_UPFRONT_PRICING_TERM_ID}
        payment_schedule_term = {"id": cls.PAYMENT_SCHEDULE_TERM_ID}
        validity_term = {"id": cls.VALIDITY_TERM_ID}
        new_legal_term = {"id": cls.NEW_LEGAL_TERM_ID}

        car_response = client.create_agreement_request(
            clientToken=generate_client_token(),
            intent="REPLACE",
            requestedTerms=[
                usage_based_pricing_term, fixed_upfront_pricing_term,
                payment_schedule_term, validity_term, new_legal_term,
            ],
            agreementProposalIdentifier=cls.NEW_AGREEMENT_PROPOSAL_IDENTIFIER,
            sourceAgreementIdentifier=agreement_id,
        )
        print("Replace agreement request created. AgreementRequestId: " + car_response["agreementRequestId"])

        aar_response = client.accept_agreement_request(
            agreementRequestId=car_response["agreementRequestId"]
        )
        print(
            "Agreement with freeTrialPricingTerm replaced with paid CCP offer. New AgreementId: "
            + aar_response["agreementId"]
        )


if __name__ == "__main__":
    ReplaceSaaSFreeTrialWithCCP.create_saas_free_trial_and_replace_with_ccp()
