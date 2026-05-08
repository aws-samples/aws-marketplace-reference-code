"""
Demonstrates how to replace an AMI agreement with usageBasedPricingTerm with a new offer while
the agreement with ConfigurableUpfrontPricingTerm (CUPT) is still active, using the
AWS Marketplace Agreement Service APIs.

Scenario: An AMI product with USAGE pricing requires two agreements:
  1. An agreement with usageBasedPricingTerm — accepted first to establish the base agreement.
  2. An agreement with configurableUpfrontPricingTerm (CUPT) — accepted after the
     usageBasedPricingTerm agreement entitlements are active.
This sample shows how to replace only the agreement with usageBasedPricingTerm with a
new offer without touching the existing agreement with configurableUpfrontPricingTerm (CUPT).

Flow:
  1. Create and accept the initial agreement request with usageBasedPricingTerm.
  2. Create and accept the agreement request with configurableUpfrontPricingTerm (CUPT)
     (after usageBasedPricingTerm agreement entitlements are active).
  3. Replace the agreement with usageBasedPricingTerm with a new offer using Intent.REPLACE.

Before running this sample, replace the placeholder constants below with values from
your AWS Marketplace offers:
  - AGREEMENT_PROPOSAL_IDENTIFIER — the agreementProposalId from the initial offer.
  - NEW_AGREEMENT_PROPOSAL_IDENTIFIER — the agreementProposalId from the new offer to replace to.
  - Term IDs (starting with term-) — found in each offer's term list.
  - SELECTOR_VALUE — duration for the agreement (e.g., P365D).
  - DIMENSION_1_KEY — dimension key defined in the CUPT term.
"""

import boto3

from utils.agreement_api_utils import (
    format_output,
    generate_client_token,
    poll_until_entitlements_available,
)


class ReplaceAmiUsageBasedPricingTermButNotCupt:

    # The agreementProposalId from the initial offer.
    AGREEMENT_PROPOSAL_IDENTIFIER = "<your-agreement-proposal-identifier>"

    # Term ID for the ConfigurableUpfrontPricingTerm in the initial offer.
    CONFIGURABLE_UPFRONT_PRICING_TERM_ID = "<your-configurable-upfront-pricing-term-id>"

    # Duration for the agreement (e.g., "P365D" for 365 days).
    SELECTOR_VALUE = "<your-selector-value>"

    # Dimension key defined in the CUPT term.
    DIMENSION_1_KEY = "<your-dimension-key>"

    # Quantity for the dimension.
    DIMENSION_1_VALUE = 1

    # Term ID for the UsageBasedPricingTerm in the initial offer.
    USAGE_TERM_ID = "<your-usage-term-id>"

    # Term ID for the LegalTerm in the initial offer.
    LEGAL_TERM_ID = "<your-legal-term-id>"

    # Term ID for the ValidityTerm in the initial offer.
    VALIDITY_TERM_ID = "<your-validity-term-id>"

    # The agreementProposalId from the new offer to replace to.
    NEW_AGREEMENT_PROPOSAL_IDENTIFIER = "<your-new-agreement-proposal-identifier>"

    # Term ID for the UsageBasedPricingTerm in the new offer.
    NEW_USAGE_TERM_ID = "<your-new-usage-term-id>"

    # Term ID for the LegalTerm in the new offer.
    NEW_LEGAL_TERM_ID = "<your-new-legal-term-id>"

    # Term ID for the ValidityTerm in the new offer.
    NEW_VALIDITY_TERM_ID = "<your-new-validity-term-id>"

    @staticmethod
    def replace_ami_usage_when_cupt_exists():
        """
        Full end-to-end flow:
        1. Create and accept an agreement request with usageBasedPricingTerm, then wait for entitlements.
        2. Create and accept an agreement request with CUPT, then wait for entitlements.
        3. Replace the agreement with usageBasedPricingTerm with a new offer
           (agreement with CUPT is unaffected).
        """
        client = boto3.client("marketplace-agreement")
        cls = ReplaceAmiUsageBasedPricingTermButNotCupt

        usage_term = {"id": cls.USAGE_TERM_ID}
        legal_term = {"id": cls.LEGAL_TERM_ID}
        validity_term = {"id": cls.VALIDITY_TERM_ID}

        # --- Step 1: Agreement with UBPT ---
        create_response = client.create_agreement_request(
            clientToken=generate_client_token(),
            intent="NEW",
            requestedTerms=[usage_term, legal_term, validity_term],
            agreementProposalIdentifier=cls.AGREEMENT_PROPOSAL_IDENTIFIER,
        )
        agreement_request_id = create_response["agreementRequestId"]
        print("Agreement request with UBPT created. AgreementRequestId: " + agreement_request_id)

        accept_response = client.accept_agreement_request(
            agreementRequestId=agreement_request_id
        )
        usage_agreement_id = accept_response["agreementId"]
        print("Agreement request with UBPT accepted. AgreementId: " + usage_agreement_id)

        # Wait for UBPT agreement entitlements to become active before creating the agreement with CUPT.
        print("Waiting for UBPT agreement entitlements to become active...")
        entitlements_response = poll_until_entitlements_available(client, usage_agreement_id)
        print("UBPT agreement entitlements are now active.")
        format_output(entitlements_response)

        # --- Step 2: Agreement with configurableUpfrontPricingTerm (CUPT) ---
        configurable_upfront_pricing_term = {
            "id": cls.CONFIGURABLE_UPFRONT_PRICING_TERM_ID,
            "configuration": {
                "configurableUpfrontPricingTermConfiguration": {
                    "selectorValue": cls.SELECTOR_VALUE,
                    "dimensions": [
                        {
                            "dimensionKey": cls.DIMENSION_1_KEY,
                            "dimensionValue": cls.DIMENSION_1_VALUE,
                        },
                    ],
                }
            },
        }

        car_response = client.create_agreement_request(
            clientToken=generate_client_token(),
            intent="NEW",
            requestedTerms=[configurable_upfront_pricing_term, legal_term, validity_term],
            agreementProposalIdentifier=cls.AGREEMENT_PROPOSAL_IDENTIFIER,
        )
        print("Agreement request with CUPT created. AgreementRequestId: " + car_response["agreementRequestId"])

        aar_response = client.accept_agreement_request(
            agreementRequestId=car_response["agreementRequestId"]
        )
        cupt_agreement_id = aar_response["agreementId"]
        print("Agreement request with CUPT accepted. AgreementId: " + cupt_agreement_id)

        # Wait for CUPT agreement entitlements to become active before replacing usage.
        print("Waiting for CUPT agreement entitlements to become active...")
        cupt_entitlements_response = poll_until_entitlements_available(client, cupt_agreement_id)
        print("CUPT agreement entitlements are now active.")
        format_output(cupt_entitlements_response)

        # --- Step 3: Replace Agreement with usageBasedPricingTerm with a new offer ---
        new_usage_term = {"id": cls.NEW_USAGE_TERM_ID}
        new_legal_term = {"id": cls.NEW_LEGAL_TERM_ID}
        new_validity_term = {"id": cls.NEW_VALIDITY_TERM_ID}

        # Use Intent.REPLACE and sourceAgreementIdentifier pointing to the usageBasedPricingTerm agreement only.
        # The agreement with configurableUpfrontPricingTerm (CUPT) is NOT affected by this replacement.
        car_replace_response = client.create_agreement_request(
            clientToken=generate_client_token(),
            intent="REPLACE",
            requestedTerms=[new_usage_term, new_legal_term, new_validity_term],
            agreementProposalIdentifier=cls.NEW_AGREEMENT_PROPOSAL_IDENTIFIER,
            sourceAgreementIdentifier=usage_agreement_id,
        )
        print("Replace agreement request created. AgreementRequestId: " + car_replace_response["agreementRequestId"])

        aar_replace_response = client.accept_agreement_request(
            agreementRequestId=car_replace_response["agreementRequestId"]
        )
        print("Agreement with UBPT replaced. New AgreementId: " + aar_replace_response["agreementId"])


if __name__ == "__main__":
    ReplaceAmiUsageBasedPricingTermButNotCupt.replace_ami_usage_when_cupt_exists()
