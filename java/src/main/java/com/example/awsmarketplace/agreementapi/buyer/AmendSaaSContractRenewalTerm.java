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
import software.amazon.awssdk.services.marketplaceagreement.model.RenewalTermConfiguration;
import software.amazon.awssdk.services.marketplaceagreement.model.RequestedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.RequestedTermConfiguration;
import utils.AgreementApiUtils;

/**
 * Demonstrates how to create a SaaS agreement with CONTRACT pricing model and then turn on
 * the auto-renewal setting using the AWS Marketplace Agreement Service APIs.
 *
 * <p>Scenario: A buyer subscribes to a SaaS product using a public offer that supports
 * auto-renewal. After acceptance, the buyer decides to amend the agreement to enable
 * auto-renewal via the RenewalTerm configuration.
 *
 * <p>Before running this sample, replace the placeholder constants below with values from
 * your AWS Marketplace offer:
 * <ul>
 *   <li>{@code AGREEMENT_PROPOSAL_IDENTIFIER} — the agreementProposalId from the offer.</li>
 *   <li>Term IDs (starting with {@code term-}) — found in the offer's term list.</li>
 *   <li>{@code SELECTOR_VALUE} — duration for the agreement (e.g., {@code P1M} for 1 month).</li>
 *   <li>{@code DIMENSION_1_KEY} — the dimension key defined in the offer.</li>
 * </ul>
 */
public class AmendSaaSContractRenewalTerm {

    // The agreementProposalId from the offer.
    private static final String AGREEMENT_PROPOSAL_IDENTIFIER = "<your-agreement-proposal-identifier>";

    // Term ID for the ConfigurableUpfrontPricingTerm in your offer.
    private static final String CONFIGURABLE_UPFRONT_PRICING_TERM_ID = "<your-configurable-upfront-pricing-term-id>";

    // Duration for the agreement (e.g., "P1M" for 1 month, "P12M" for 1 year).
    private static final String SELECTOR_VALUE = "<your-selector-value>";

    // The dimension key defined in your offer.
    private static final String DIMENSION_1_KEY = "<your-dimension-key>";

    // Quantity for the dimension.
    private static final int DIMENSION_1_VALUE = 1;

    // Term ID for the RenewalTerm in your offer.
    private static final String RENEWAL_TERM_ID = "<your-renewal-term-id>";

    // Term ID for the LegalTerm in your offer.
    private static final String LEGAL_TERM_ID = "<your-legal-term-id>";

    // Term ID for the SupportTerm in your offer.
    private static final String SUPPORT_TERM_ID = "<your-support-term-id>";

    public static void main(String[] args) {
        amendSaaSContractAgreementRenewalTerm();
    }

    /**
     * Full end-to-end flow:
     * 1. Create a SaaS agreement with CONTRACT pricing model with auto-renewal disabled.
     * 2. Wait for entitlements to become active.
     * 3. Amend the agreement to enable auto-renewal.
     */
    private static void amendSaaSContractAgreementRenewalTerm() {
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

        // Initial agreement: auto-renewal disabled.
        RequestedTerm renewalTerm = RequestedTerm.builder()
                .id(RENEWAL_TERM_ID)
                .configuration(RequestedTermConfiguration.fromRenewalTermConfiguration(
                        RenewalTermConfiguration.builder()
                                .enableAutoRenew(false)
                                .build()))
                .build();

        RequestedTerm legalTerm = RequestedTerm.builder().id(LEGAL_TERM_ID).build();
        RequestedTerm supportTerm = RequestedTerm.builder().id(SUPPORT_TERM_ID).build();

        // --- Create and accept the initial SaaS agreement request with CONTRACT pricing model ---
        CreateAgreementRequestRequest createAgreementRequestRequest =
                CreateAgreementRequestRequest.builder()
                        .clientToken(AgreementApiUtils.generateClientToken())
                        .intent(Intent.NEW)
                        .requestedTerms(configurableUpfrontPricingTerm, renewalTerm, legalTerm, supportTerm)
                        .agreementProposalIdentifier(AGREEMENT_PROPOSAL_IDENTIFIER)
                        .build();
        CreateAgreementRequestResponse createAgreementRequestResponse =
                marketplaceAgreementClient.createAgreementRequest(createAgreementRequestRequest);
        System.out.println("Agreement request created. AgreementRequestId: " + createAgreementRequestResponse.agreementRequestId());

        AcceptAgreementRequestRequest acceptAgreementRequestRequest =
                AcceptAgreementRequestRequest.builder()
                        .agreementRequestId(createAgreementRequestResponse.agreementRequestId())
                        .build();
        AcceptAgreementRequestResponse acceptAgreementRequestResponse =
                marketplaceAgreementClient.acceptAgreementRequest(acceptAgreementRequestRequest);
        System.out.println("Agreement request accepted. AgreementId: " + acceptAgreementRequestResponse.agreementId());

        // Wait for entitlements to become active before amending.
        System.out.println("Waiting for entitlements to become active...");
        GetAgreementEntitlementsResponse entitlementsResponse = AgreementApiUtils.pollUntilEntitlementsAvailable(
                marketplaceAgreementClient, acceptAgreementRequestResponse.agreementId());
        System.out.println("Entitlements are now active.");
        AgreementApiUtils.formatOutput(entitlementsResponse);

        // --- Amend: enable auto-renewal ---
        RequestedTerm renewalTermAmended = RequestedTerm.builder()
                .id(RENEWAL_TERM_ID)
                .configuration(RequestedTermConfiguration.fromRenewalTermConfiguration(
                        RenewalTermConfiguration.builder()
                                .enableAutoRenew(true)
                                .build()))
                .build();

        // Use Intent.AMEND and sourceAgreementIdentifier to target the existing agreement.
        CreateAgreementRequestRequest carRequest =
                CreateAgreementRequestRequest.builder()
                        .clientToken(AgreementApiUtils.generateClientToken())
                        .intent(Intent.AMEND)
                        .requestedTerms(configurableUpfrontPricingTerm, renewalTermAmended, legalTerm, supportTerm)
                        .sourceAgreementIdentifier(acceptAgreementRequestResponse.agreementId())
                        .build();
        CreateAgreementRequestResponse carResponse =
                marketplaceAgreementClient.createAgreementRequest(carRequest);
        System.out.println("Amend agreement request created. AgreementRequestId: " + carResponse.agreementRequestId());

        AcceptAgreementRequestRequest aarRequest =
                AcceptAgreementRequestRequest.builder()
                        .agreementRequestId(carResponse.agreementRequestId())
                        .build();
        AcceptAgreementRequestResponse aarResponse =
                marketplaceAgreementClient.acceptAgreementRequest(aarRequest);
        System.out.println("Amendment accepted. Auto-renewal enabled. New AgreementId: " + aarResponse.agreementId());
    }
}
