"""
Demonstrates how to associate a purchase order reference with a SaaS agreement with CONTRACT
pricing model using the AWS Marketplace Agreement Service APIs.

Scenario: A buyer creates a SaaS agreement request with CONTRACT pricing model and provides
a purchase order reference in AcceptAgreementRequest. After acceptance, the buyer lists the
resulting charges via ListAgreementCharges and associates the purchase order reference with a
specific charge via UpdatePurchaseOrders.

Before running this sample, replace the placeholder constants below with values from
your AWS Marketplace offer:
  - AGREEMENT_PROPOSAL_IDENTIFIER — the agreementProposalId from the offer.
  - Term IDs (starting with term-) — found in the offer's term list.
  - SELECTOR_VALUE — duration for the agreement.
  - DIMENSION_1_KEY — dimension key defined in the offer.
  - PURCHASE_ORDER_REFERENCE — your internal purchase order number (e.g., po-123456).
"""

import boto3

from utils.agreement_api_utils import format_output, generate_client_token


class UpdatePurchaseOrdersAfterAgreementAcceptance:

    # Your internal purchase order reference number (e.g., "po-123456").
    PURCHASE_ORDER_REFERENCE = "po-123456"

    # The agreementProposalId from the offer.
    AGREEMENT_PROPOSAL_IDENTIFIER = "<your-agreement-proposal-identifier>"

    # Term ID for the ConfigurableUpfrontPricingTerm in your offer.
    CONFIGURABLE_UPFRONT_PRICING_TERM_ID = "<your-configurable-upfront-pricing-term-id>"

    # Duration for the agreement (e.g., "P366D" for 366 days).
    SELECTOR_VALUE = "<your-selector-value>"

    # Dimension key and quantity defined in your offer.
    DIMENSION_1_KEY = "<your-dimension-key>"
    DIMENSION_1_VALUE = 1

    # Term ID for the LegalTerm in your offer.
    LEGAL_TERM_ID = "<your-legal-term-id>"

    # Term ID for the ValidityTerm in your offer.
    VALIDITY_TERM_ID = "<your-validity-term-id>"

    @staticmethod
    def list_agreement_charges_and_update_purchase_orders():
        """
        Full end-to-end flow:
        1. Create a SaaS agreement with CONTRACT pricing model with a purchase order reference.
        2. List charges to retrieve charge IDs and revisions.
        3. Associate the purchase order reference with a specific charge via UpdatePurchaseOrders.
        4. List charges again to confirm the update.
        """
        client = boto3.client("marketplace-agreement")
        cls = UpdatePurchaseOrdersAfterAgreementAcceptance

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

        legal_term = {"id": cls.LEGAL_TERM_ID}
        validity_term = {"id": cls.VALIDITY_TERM_ID}

        # --- Create Agreement ---
        create_response = client.create_agreement_request(
            clientToken=generate_client_token(),
            intent="NEW",
            requestedTerms=[configurable_upfront_pricing_term, legal_term, validity_term],
            agreementProposalIdentifier=cls.AGREEMENT_PROPOSAL_IDENTIFIER,
        )
        agreement_request_id = create_response["agreementRequestId"]
        print("Agreement request created. AgreementRequestId: " + agreement_request_id)

        # --- Accept Agreement Request with Purchase Order ---
        # The chargeId is available from the CAR response's chargeSummary.expectedCharges.
        charge_id = create_response["chargeSummary"]["expectedCharges"][0]["id"]
        accept_response = client.accept_agreement_request(
            agreementRequestId=agreement_request_id,
            purchaseOrders=[
                {
                    "chargeId": charge_id,
                    "purchaseOrderReference": cls.PURCHASE_ORDER_REFERENCE,
                }
            ],
        )
        agreement_id = accept_response["agreementId"]
        print(
            "Agreement request accepted with purchase order reference '"
            + cls.PURCHASE_ORDER_REFERENCE + "'. AgreementId: " + agreement_id
        )

        # --- List Agreement Charges ---
        list_charges_response = client.list_agreement_charges(agreementId=agreement_id)
        print("All charges for agreement " + agreement_id + ":")
        format_output(list_charges_response)

        # --- Update Purchase Order ---
        first_charge = list_charges_response["items"][0]
        client.update_purchase_orders(
            purchaseOrders=[
                {
                    "agreementId": agreement_id,
                    "purchaseOrderReference": cls.PURCHASE_ORDER_REFERENCE,
                    "chargeRevision": first_charge["revision"],
                    "chargeId": first_charge["id"],
                }
            ],
        )
        print(
            "Purchase order reference '" + cls.PURCHASE_ORDER_REFERENCE
            + "' updated for ChargeId: " + first_charge["id"]
        )

        # --- Verify Update ---
        lac_response = client.list_agreement_charges(agreementId=agreement_id)
        print("Verified updated charge:")
        format_output(lac_response["items"][0])


if __name__ == "__main__":
    UpdatePurchaseOrdersAfterAgreementAcceptance.list_agreement_charges_and_update_purchase_orders()
