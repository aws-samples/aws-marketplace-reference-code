"""
Demonstrates how to create a SaaS agreement with CONTRACT pricing model and then turn on
the auto-renewal setting using the AWS Marketplace Agreement Service APIs.

Scenario: A buyer subscribes to a SaaS product using a public offer that supports
auto-renewal. After acceptance, the buyer decides to amend the agreement to enable
auto-renewal via the RenewalTerm configuration.

Before running this sample, replace the placeholder constants below with values from
your AWS Marketplace offer:
  - AGREEMENT_PROPOSAL_IDENTIFIER — the agreementProposalId from the offer.
  - Term IDs (starting with term-) — found in the offer's term list.
  - SELECTOR_VALUE — duration for the agreement (e.g., P1M for 1 month).
  - DIMENSION_1_KEY — the dimension key defined in the offer.
"""

import boto3

from utils.agreement_api_utils import (
    format_output,
    generate_client_token,
    poll_until_entitlements_available,
)


class AmendSaaSContractRenewalTerm:

    # The agreementProposalId from the offer.
    AGREEMENT_PROPOSAL_IDENTIFIER = "<your-agreement-proposal-identifier>"

    # Term ID for the ConfigurableUpfrontPricingTerm in your offer.
    CONFIGURABLE_UPFRONT_PRICING_TERM_ID = "<your-configurable-upfront-pricing-term-id>"

    # Duration for the agreement (e.g., "P1M" for 1 month, "P12M" for 1 year).
    SELECTOR_VALUE = "<your-selector-value>"

    # The dimension key defined in your offer.
    DIMENSION_1_KEY = "<your-dimension-key>"

    # Quantity for the dimension.
    DIMENSION_1_VALUE = 1

    # Term ID for the RenewalTerm in your offer.
    RENEWAL_TERM_ID = "<your-renewal-term-id>"

    # Term ID for the LegalTerm in your offer.
    LEGAL_TERM_ID = "<your-legal-term-id>"

    # Term ID for the SupportTerm in your offer.
    SUPPORT_TERM_ID = "<your-support-term-id>"

    @staticmethod
    def amend_saas_contract_agreement_renewal_term():
        """
        Full end-to-end flow:
        1. Create a SaaS agreement with CONTRACT pricing model with auto-renewal disabled.
        2. Wait for entitlements to become active.
        3. Amend the agreement to enable auto-renewal.
        """
        client = boto3.client("marketplace-agreement")
        cls = AmendSaaSContractRenewalTerm

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

        # Initial agreement: auto-renewal disabled.
        renewal_term = {
            "id": cls.RENEWAL_TERM_ID,
            "configuration": {
                "renewalTermConfiguration": {
                    "enableAutoRenew": False,
                }
            },
        }

        legal_term = {"id": cls.LEGAL_TERM_ID}
        support_term = {"id": cls.SUPPORT_TERM_ID}

        # --- Create and accept the initial SaaS agreement request with CONTRACT pricing model ---
        create_response = client.create_agreement_request(
            clientToken=generate_client_token(),
            intent="NEW",
            requestedTerms=[configurable_upfront_pricing_term, renewal_term, legal_term, support_term],
            agreementProposalIdentifier=cls.AGREEMENT_PROPOSAL_IDENTIFIER,
        )
        agreement_request_id = create_response["agreementRequestId"]
        print("Agreement request created. AgreementRequestId: " + agreement_request_id)

        accept_response = client.accept_agreement_request(
            agreementRequestId=agreement_request_id
        )
        agreement_id = accept_response["agreementId"]
        print("Agreement request accepted. AgreementId: " + agreement_id)

        # Wait for entitlements to become active before amending.
        print("Waiting for entitlements to become active...")
        entitlements_response = poll_until_entitlements_available(client, agreement_id)
        print("Entitlements are now active.")
        format_output(entitlements_response)

        # --- Amend: enable auto-renewal ---
        renewal_term_amended = {
            "id": cls.RENEWAL_TERM_ID,
            "configuration": {
                "renewalTermConfiguration": {
                    "enableAutoRenew": True,
                }
            },
        }

        # Use Intent.AMEND and sourceAgreementIdentifier to target the existing agreement.
        car_response = client.create_agreement_request(
            clientToken=generate_client_token(),
            intent="AMEND",
            requestedTerms=[configurable_upfront_pricing_term, renewal_term_amended, legal_term, support_term],
            sourceAgreementIdentifier=agreement_id,
        )
        print("Amend agreement request created. AgreementRequestId: " + car_response["agreementRequestId"])

        aar_response = client.accept_agreement_request(
            agreementRequestId=car_response["agreementRequestId"]
        )
        print("Amendment accepted. Auto-renewal enabled. New AgreementId: " + aar_response["agreementId"])


if __name__ == "__main__":
    AmendSaaSContractRenewalTerm.amend_saas_contract_agreement_renewal_term()
