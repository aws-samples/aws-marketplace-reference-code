// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi.buyer;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptAgreementRequestRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptAgreementRequestResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.ConfigurableUpfrontPricingTermConfiguration;
import software.amazon.awssdk.services.marketplaceagreement.model.CreateAgreementRequestRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.CreateAgreementRequestResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.Dimension;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementEntitlementsResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.Intent;
import software.amazon.awssdk.services.marketplaceagreement.model.RequestedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.RequestedTermConfiguration;
import utils.AgreementApiUtils;

/**
 * Demonstrates how to create an AMI agreement with ConfigurableUpfrontPricingTerm and then amend the dimension quantity
 * using the AWS Marketplace Agreement Service APIs.
 *
 * <p>Scenario: An AMI product with USAGE pricing requires two agreements:
 * <ol>
 *   <li>An agreement with <b>usageBasedPricingTerm (UBPT)</b> — accepted first to establish the base agreement.</li>
 *   <li>An agreement with <b>configurableUpfrontPricingTerm (CUPT)</b> — accepted after the UBPT agreement entitlements are active.</li>
 * </ol>
 * Once both agreement entitlements are available, this sample shows how to <b>amend</b> the agreement
 * with configurableUpfrontPricingTerm (CUPT) to increase the dimension quantity.
 *
 * <p>Before running this sample, replace the placeholder constants below with values from
 * your AWS Marketplace offer:
 * <ul>
 *   <li>{@code AGREEMENT_PROPOSAL_IDENTIFIER} — the agreementProposalId from the offer.</li>
 *   <li>Term IDs (starting with {@code term-}) — found in the offer's term list.</li>
 *   <li>{@code SELECTOR_VALUE} —  duration for the agreement
 *       (e.g., {@code P365D} for one year).</li>
 *   <li>{@code DIMENSION_1_KEY} — the dimension key defined in the offer (e.g., instance type).</li>
 *   <li>{@code DIMENSION_1_VALUE} — initial quantity; {@code NEW_DIMENSION_1_VALUE} — amended quantity.</li>
 * </ul>
 */
public class AmendAmiConfigurableUpfrontPricingTermForUsagePricingModel {

    // The agreementProposalId from the offer.
    private static final String AGREEMENT_PROPOSAL_IDENTIFIER = "<your-agreement-proposal-identifier>";

    // Term ID for the ConfigurableUpfrontPricingTerm in your offer.
    private static final String CONFIGURABLE_UPFRONT_PRICING_TERM_ID = "<your-configurable-upfront-pricing-term-id>";

    // Duration for the agreement (e.g., "P365D" for 365 days).
    private static final String SELECTOR_VALUE = "<your-selector-value>";

    // The dimension key defined in your offer (e.g., an EC2 instance type like "c6gn.medium").
    private static final String DIMENSION_1_KEY = "<your-dimension-key>";

    // Initial quantity for the dimension.
    private static final int DIMENSION_1_VALUE = 1;

    // Term ID for the UsageBasedPricingTerm in your offer.
    private static final String USAGE_TERM_ID = "<your-usage-term-id>";

    // Term ID for the LegalTerm in your offer.
    private static final String LEGAL_TERM_ID = "<your-legal-term-id>";

    // Term ID for the ValidityTerm in your offer.
    private static final String VALIDITY_TERM_ID = "<your-validity-term-id>";

    // New quantity to use when amending the dimension of CUPT.
    private static final int NEW_DIMENSION_1_VALUE = 5;

    public static void main(String[] args) {
        amendAmiCUPTAgreement();
    }

    /**
     * Full end-to-end flow:
     * 1. Create and accept an agreement request with usageBasedPricingTerm.
     * 2. Wait for entitlements to become active, then create and accept an agreement request with configurableUpfrontPricingTerm (CUPT).
     * 3. Wait for CUPT entitlements to become active, then amend the dimension quantity.
     */
    private static void amendAmiCUPTAgreement() {
        MarketplaceAgreementClient marketplaceAgreementClient =
                MarketplaceAgreementClient.builder()
                        .httpClient(ApacheHttpClient.builder().build())
                        .credentialsProvider(ProfileCredentialsProvider.create())
                        .build();

        RequestedTerm usageTerm = RequestedTerm.builder()
                .id(USAGE_TERM_ID)
                .build();
        RequestedTerm legalTerm = RequestedTerm.builder()
                .id(LEGAL_TERM_ID)
                .build();
        RequestedTerm validityTerm = RequestedTerm.builder()
                .id(VALIDITY_TERM_ID)
                .build();

        // --- Agreement with UBPT ---
        CreateAgreementRequestRequest createAgreementRequestRequest =
                CreateAgreementRequestRequest.builder()
                        .clientToken(AgreementApiUtils.generateClientToken())
                        .intent(Intent.NEW)
                        .requestedTerms(usageTerm, legalTerm, validityTerm)
                        .agreementProposalIdentifier(AGREEMENT_PROPOSAL_IDENTIFIER)
                        .build();
        CreateAgreementRequestResponse createAgreementRequestResponse =
                marketplaceAgreementClient.createAgreementRequest(createAgreementRequestRequest);
        System.out.println("Agreement request with UBPT created. AgreementRequestId: " + createAgreementRequestResponse.agreementRequestId());

        AcceptAgreementRequestRequest acceptAgreementRequestRequest =
                AcceptAgreementRequestRequest.builder()
                        .agreementRequestId(createAgreementRequestResponse.agreementRequestId())
                        .build();
        AcceptAgreementRequestResponse acceptAgreementRequestResponse =
                marketplaceAgreementClient.acceptAgreementRequest(acceptAgreementRequestRequest);
        System.out.println("Agreement request with UBPT accepted. AgreementId: " + acceptAgreementRequestResponse.agreementId());

        // Wait for entitlements to become active before creating the agreement with CUPT.
        System.out.println("Waiting for UBPT agreement entitlements to become active...");
        GetAgreementEntitlementsResponse entitlementsResponse = AgreementApiUtils.pollUntilEntitlementsAvailable(
                marketplaceAgreementClient, acceptAgreementRequestResponse.agreementId());
        System.out.println("UBPT agreement entitlements are now active.");
        AgreementApiUtils.formatOutput(entitlementsResponse);

        // --- Agreement with configurableUpfrontPricingTerm (CUPT) ---
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

        CreateAgreementRequestRequest carRequest =
                CreateAgreementRequestRequest.builder()
                        .clientToken(AgreementApiUtils.generateClientToken())
                        .intent(Intent.NEW)
                        .requestedTerms(configurableUpfrontPricingTerm, legalTerm, validityTerm)
                        .agreementProposalIdentifier(AGREEMENT_PROPOSAL_IDENTIFIER)
                        .build();
        CreateAgreementRequestResponse carResponse =
                marketplaceAgreementClient.createAgreementRequest(carRequest);
        System.out.println("Agreement request with CUPT created. AgreementRequestId: " + carResponse.agreementRequestId());

        AcceptAgreementRequestRequest aarRequest =
                AcceptAgreementRequestRequest.builder()
                        .agreementRequestId(carResponse.agreementRequestId())
                        .build();
        AcceptAgreementRequestResponse aarResponse =
                marketplaceAgreementClient.acceptAgreementRequest(aarRequest);
        final String cuptAgreementId = aarResponse.agreementId();
        System.out.println("Agreement request with CUPT accepted. AgreementId: " + cuptAgreementId);

        // Wait for entitlements to become active before amending.
        System.out.println("Waiting for CUPT agreement entitlements to become active...");
        GetAgreementEntitlementsResponse cuptEntitlementsResponse = AgreementApiUtils.pollUntilEntitlementsAvailable(
                marketplaceAgreementClient, cuptAgreementId);
        System.out.println("CUPT agreement entitlements are now active.");
        AgreementApiUtils.formatOutput(cuptEntitlementsResponse);

        // --- Amend Agreement with CUPT ---
        // Increase the dimension quantity using Intent.AMEND and sourceAgreementIdentifier.
        RequestedTerm newConfig = RequestedTerm.builder()
                .id(CONFIGURABLE_UPFRONT_PRICING_TERM_ID)
                .configuration(RequestedTermConfiguration.fromConfigurableUpfrontPricingTermConfiguration(
                        ConfigurableUpfrontPricingTermConfiguration.builder()
                                .selectorValue(SELECTOR_VALUE)
                                .dimensions(Dimension.builder()
                                                    .dimensionKey(DIMENSION_1_KEY)
                                                    .dimensionValue(NEW_DIMENSION_1_VALUE) // Increase quantity for this dimension key
                                                    .build())
                                .build()))
                .build();

        CreateAgreementRequestRequest carAmendRequest =
                CreateAgreementRequestRequest.builder()
                        .clientToken(AgreementApiUtils.generateClientToken())
                        .intent(Intent.AMEND)
                        .requestedTerms(newConfig, legalTerm, validityTerm)
                        .sourceAgreementIdentifier(cuptAgreementId)
                        .build();
        CreateAgreementRequestResponse carAmendResponse =
                marketplaceAgreementClient.createAgreementRequest(carAmendRequest);
        System.out.println("Amendment of CUPT agreement request created. AgreementRequestId: " + carAmendResponse.agreementRequestId());

        AcceptAgreementRequestRequest aarAmendRequest =
                AcceptAgreementRequestRequest.builder()
                        .agreementRequestId(carAmendResponse.agreementRequestId())
                        .build();
        AcceptAgreementRequestResponse aarAmendResponse =
                marketplaceAgreementClient.acceptAgreementRequest(aarAmendRequest);
        System.out.println("Amendment accepted. New AgreementId: " + aarAmendResponse.agreementId());
    }
}
