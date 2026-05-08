"""
Demonstrates how to create a SaaS agreement with usageBasedPricingTerm (UBPT) and then replace it
with a new offer using the AWS Marketplace Agreement Service APIs.

Scenario: A buyer subscribes to a SaaS product with UsageBasedPricingTerm.
The buyer then converts to a different offer by replacing the existing agreement.

Flow:
  1. Create and accept the initial agreement request with UBPT.
  2. Wait for entitlements to become active.
  3. Replace the agreement with a new offer using Intent.REPLACE.
  4. Cancel the new agreement using CancelAgreement.

Before running this sample, replace the placeholder constants below with values from
your AWS Marketplace offers:
  - AGREEMENT_PROPOSAL_IDENTIFIER — the agreementProposalId from the initial offer.
  - NEW_AGREEMENT_PROPOSAL_IDENTIFIER — the agreementProposalId from the new offer to replace to.
  - Term IDs (starting with term-) — found in each offer's term list.
"""

import boto3

from utils.agreement_api_utils import (
    format_output,
    generate_client_token,
    poll_until_entitlements_available,
)


class ReplaceSaaSUsageBasedPricingTermAndCancel:

    # The agreementProposalId from the initial offer.
    AGREEMENT_PROPOSAL_IDENTIFIER = "<your-agreement-proposal-identifier>"

    # Term ID for the UsageBasedPricingTerm in the initial offer.
    USAGE_BASED_PRICING_TERM_ID = "<your-usage-based-pricing-term-id>"

    # Term ID for the ValidityTerm in the initial offer.
    VALIDITY_TERM_ID = "<your-validity-term-id>"

    # Term ID for the LegalTerm in the initial offer.
    LEGAL_TERM_ID = "<your-legal-term-id>"

    # The agreementProposalId from the new offer to replace to.
    NEW_AGREEMENT_PROPOSAL_IDENTIFIER = "<your-new-agreement-proposal-identifier>"

    # Term ID for the UsageBasedPricingTerm in the new offer.
    NEW_USAGE_BASED_PRICING_TERM_ID = "<your-new-usage-based-pricing-term-id>"

    # Term ID for the ValidityTerm in the new offer.
    NEW_VALIDITY_TERM_ID = "<your-new-validity-term-id>"

    # Term ID for the LegalTerm in the new offer.
    NEW_LEGAL_TERM_ID = "<your-new-legal-term-id>"

    @staticmethod
    def replace_saas_ubpt_and_cancel():
        """
        Full end-to-end flow:
        1. Create and accept the initial agreement request with UsageBasedPricingTerm.
        2. Wait for entitlements to become active.
        3. Replace the agreement with a new offer.
        4. Cancel the new agreement.
        """
        client = boto3.client("marketplace-agreement")
        cls = ReplaceSaaSUsageBasedPricingTermAndCancel

        usage_based_pricing_term = {"id": cls.USAGE_BASED_PRICING_TERM_ID}
        validity_term = {"id": cls.VALIDITY_TERM_ID}
        legal_term = {"id": cls.LEGAL_TERM_ID}

        # --- Step 1: Create and accept the initial UBPT agreement request ---
        create_response = client.create_agreement_request(
            clientToken=generate_client_token(),
            intent="NEW",
            requestedTerms=[usage_based_pricing_term, validity_term, legal_term],
            agreementProposalIdentifier=cls.AGREEMENT_PROPOSAL_IDENTIFIER,
        )
        agreement_request_id = create_response["agreementRequestId"]
        print("Agreement request with UBPT created. AgreementRequestId: " + agreement_request_id)

        accept_response = client.accept_agreement_request(
            agreementRequestId=agreement_request_id
        )
        agreement_id = accept_response["agreementId"]
        print("Agreement request with UBPT accepted. AgreementId: " + agreement_id)

        # Wait for entitlements to become active before replacing.
        print("Waiting for entitlements to become active...")
        entitlements_response = poll_until_entitlements_available(client, agreement_id)
        print("Entitlements are now active.")
        format_output(entitlements_response)

        # --- Step 2: Replace the UBPT agreement with a new offer ---
        # Use Intent.REPLACE and sourceAgreementIdentifier to replace the existing agreement.
        new_usage_based_pricing_term = {"id": cls.NEW_USAGE_BASED_PRICING_TERM_ID}
        new_validity_term = {"id": cls.NEW_VALIDITY_TERM_ID}
        new_legal_term = {"id": cls.NEW_LEGAL_TERM_ID}

        car_response = client.create_agreement_request(
            clientToken=generate_client_token(),
            intent="REPLACE",
            requestedTerms=[new_usage_based_pricing_term, new_validity_term, new_legal_term],
            agreementProposalIdentifier=cls.NEW_AGREEMENT_PROPOSAL_IDENTIFIER,
            sourceAgreementIdentifier=agreement_id,
        )
        print("Replace agreement request created. AgreementRequestId: " + car_response["agreementRequestId"])

        aar_response = client.accept_agreement_request(
            agreementRequestId=car_response["agreementRequestId"]
        )
        agreement_id_with_new_offer = aar_response["agreementId"]
        print("UBPT agreement replaced. New AgreementId: " + agreement_id_with_new_offer)

        # --- Step 3: Cancel the new agreement ---
        client.cancel_agreement(agreementId=agreement_id_with_new_offer)
        print("The new agreement has been cancelled. AgreementId: " + agreement_id_with_new_offer)


if __name__ == "__main__":
    ReplaceSaaSUsageBasedPricingTermAndCancel.replace_saas_ubpt_and_cancel()
