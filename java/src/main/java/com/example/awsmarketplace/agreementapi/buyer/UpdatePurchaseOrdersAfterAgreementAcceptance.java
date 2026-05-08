// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi.buyer;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptAgreementRequestRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptAgreementRequestResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.Charge;
import software.amazon.awssdk.services.marketplaceagreement.model.ConfigurableUpfrontPricingTermConfiguration;
import software.amazon.awssdk.services.marketplaceagreement.model.CreateAgreementRequestRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.CreateAgreementRequestResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.Dimension;
import software.amazon.awssdk.services.marketplaceagreement.model.Intent;
import software.amazon.awssdk.services.marketplaceagreement.model.ListAgreementChargesRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.ListAgreementChargesResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.PurchaseOrder;
import software.amazon.awssdk.services.marketplaceagreement.model.RequestedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.RequestedTermConfiguration;
import software.amazon.awssdk.services.marketplaceagreement.model.UpdatePurchaseOrdersRequest;
import utils.AgreementApiUtils;

/**
 * Demonstrates how to associate a purchase order reference with a SaaS agreement with CONTRACT pricing model
 * using the AWS Marketplace Agreement Service APIs.
 *
 * <p>Scenario: A buyer creates a SaaS agreement request with CONTRACT pricing model and provides a purchase order
 * reference in AcceptAgreementRequest. After acceptance, the buyer lists the resulting
 * charges via ListAgreementCharges and associates the purchase order reference with a
 * specific charge via UpdatePurchaseOrders.
 *
 * <p>Before running this sample, replace the placeholder constants below with values from
 * your AWS Marketplace offer:
 * <ul>
 *   <li>{@code AGREEMENT_PROPOSAL_IDENTIFIER} — the agreementProposalId from the offer.</li>
 *   <li>Term IDs (starting with {@code term-}) — found in the offer's term list.</li>
 *   <li>{@code SELECTOR_VALUE} — duration for the agreement.</li>
 *   <li>{@code DIMENSION_1_KEY} — dimension key defined in the offer.</li>
 *   <li>{@code PURCHASE_ORDER_REFERENCE} — your internal purchase order number (e.g., {@code po-123456}).</li>
 * </ul>
 */
public class UpdatePurchaseOrdersAfterAgreementAcceptance {

    // Your internal purchase order reference number (e.g., "po-123456").
    private static final String PURCHASE_ORDER_REFERENCE = "po-123456";

    // The agreementProposalId from the offer.
    private static final String AGREEMENT_PROPOSAL_IDENTIFIER = "<your-agreement-proposal-identifier>";

    // Term ID for the ConfigurableUpfrontPricingTerm in your offer.
    private static final String CONFIGURABLE_UPFRONT_PRICING_TERM_ID = "<your-configurable-upfront-pricing-term-id>";

    // Duration for the agreement (e.g., "P366D" for 366 days).
    private static final String SELECTOR_VALUE = "<your-selector-value>";

    // Dimension key and quantity defined in your offer.
    private static final String DIMENSION_1_KEY = "<your-dimension-key>";
    private static final int DIMENSION_1_VALUE = 1;

    // Term ID for the LegalTerm in your offer.
    private static final String LEGAL_TERM_ID = "<your-legal-term-id>";

    // Term ID for the ValidityTerm in your offer.
    private static final String VALIDITY_TERM_ID = "<your-validity-term-id>";

    public static void main(String[] args) {
        listAgreementChargesAndUpdatePurchaseOrders();
    }

    /**
     * Full end-to-end flow:
     * 1. Create a SaaS agreement with CONTRACT pricing model with a purchase order reference.
     * 2. List charges to retrieve charge IDs and revisions.
     * 3. Associate the purchase order reference with a specific charge via UpdatePurchaseOrders.
     * 4. List charges again to confirm the update.
     */
    private static void listAgreementChargesAndUpdatePurchaseOrders() {
        MarketplaceAgreementClient marketplaceAgreementClient =
                MarketplaceAgreementClient.builder()
                        .httpClient(ApacheHttpClient.builder().build())
                        .credentialsProvider(ProfileCredentialsProvider.create())
                        .build();

        RequestedTerm configurableUpfrontPricingTerm = RequestedTerm.builder()
                .id(CONFIGURABLE_UPFRONT_PRICING_TERM_ID)
                .configuration(RequestedTermConfiguration.fromConfigurableUpfrontPricingTermConfiguration(
                        ConfigurableUpfrontPricingTermConfiguration.builder()
                                .selectorValue(SELECTOR_VALUE)
                                .dimensions(Dimension.builder()
                                                    .dimensionKey(DIMENSION_1_KEY)
                                                    .dimensionValue(DIMENSION_1_VALUE)
                                                    .build())
                                .build()))
                .build();

        RequestedTerm legalTerm = RequestedTerm.builder().id(LEGAL_TERM_ID).build();
        RequestedTerm validityTerm = RequestedTerm.builder().id(VALIDITY_TERM_ID).build();

        // --- Create Agreement ---
        CreateAgreementRequestRequest createAgreementRequestRequest =
                CreateAgreementRequestRequest.builder()
                        .clientToken(AgreementApiUtils.generateClientToken())
                        .intent(Intent.NEW)
                        .requestedTerms(configurableUpfrontPricingTerm, legalTerm, validityTerm)
                        .agreementProposalIdentifier(AGREEMENT_PROPOSAL_IDENTIFIER)
                        .build();
        CreateAgreementRequestResponse createAgreementRequestResponse =
                marketplaceAgreementClient.createAgreementRequest(createAgreementRequestRequest);
        System.out.println("Agreement request created. AgreementRequestId: " + createAgreementRequestResponse.agreementRequestId());

        // --- Accept Agreement Request with Purchase Order ---
        // The chargeId is available from the CAR response's chargeSummary.expectedCharges.
        String chargeId = createAgreementRequestResponse.chargeSummary().expectedCharges().get(0).id();
        PurchaseOrder purchaseOrderAtAcceptance = PurchaseOrder.builder()
                .chargeId(chargeId)
                .purchaseOrderReference(PURCHASE_ORDER_REFERENCE)
                .build();
        AcceptAgreementRequestRequest acceptAgreementRequestRequest =
                AcceptAgreementRequestRequest.builder()
                        .agreementRequestId(createAgreementRequestResponse.agreementRequestId())
                        .purchaseOrders(purchaseOrderAtAcceptance)
                        .build();
        AcceptAgreementRequestResponse acceptAgreementRequestResponse =
                marketplaceAgreementClient.acceptAgreementRequest(acceptAgreementRequestRequest);
        final String agreementId = acceptAgreementRequestResponse.agreementId();
        System.out.println("Agreement request accepted with purchase order reference '" + PURCHASE_ORDER_REFERENCE
                + "'. AgreementId: " + agreementId);

        // --- List Agreement Charges ---
        ListAgreementChargesRequest listAgreementChargesRequest =
                ListAgreementChargesRequest.builder()
                        .agreementId(agreementId)
                        .build();
        ListAgreementChargesResponse listAgreementChargesResponse =
                marketplaceAgreementClient.listAgreementCharges(listAgreementChargesRequest);

        System.out.println("All charges for agreement " + agreementId + ":");
        AgreementApiUtils.formatOutput(listAgreementChargesResponse);

        // --- Update Purchase Order ---
        Charge firstCharge = listAgreementChargesResponse.items().get(0);
        PurchaseOrder purchaseOrder = PurchaseOrder.builder()
                .agreementId(agreementId)
                .purchaseOrderReference(PURCHASE_ORDER_REFERENCE)
                .chargeRevision(firstCharge.revision())
                .chargeId(firstCharge.id())
                .build();
        UpdatePurchaseOrdersRequest updatePurchaseOrdersRequest =
                UpdatePurchaseOrdersRequest.builder()
                        .purchaseOrders(purchaseOrder)
                        .build();
        marketplaceAgreementClient.updatePurchaseOrders(updatePurchaseOrdersRequest);
        System.out.println("Purchase order reference '" + PURCHASE_ORDER_REFERENCE
                + "' updated for ChargeId: " + firstCharge.id());

        // --- Verify Update ---
        ListAgreementChargesRequest lacRequest =
                ListAgreementChargesRequest.builder()
                        .agreementId(agreementId)
                        .build();
        ListAgreementChargesResponse lacResponse =
                marketplaceAgreementClient.listAgreementCharges(lacRequest);
        System.out.println("Verified updated charge:");
        AgreementApiUtils.formatOutput(lacResponse.items().get(0));
    }
}
