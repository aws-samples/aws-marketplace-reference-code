// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi.buyer.agreementRequest;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.ChargeSummary;
import software.amazon.awssdk.services.marketplaceagreement.model.ExpectedCharge;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementRequestRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementRequestResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.ItemizedCharge;
import software.amazon.awssdk.services.marketplaceagreement.model.Resource;

public class GetAgreementRequest {

    private static final String AGREEMENT_REQUEST_ID = "<AGREEMENT REQUEST ID HERE>";

    public static void main(String[] args) {
        getAgreementRequest();
    }

    private static void getAgreementRequest() {
        MarketplaceAgreementClient marketplaceAgreementClient =
                MarketplaceAgreementClient.builder()
                        .httpClient(ApacheHttpClient.builder().build())
                        .credentialsProvider(ProfileCredentialsProvider.create())
                        .build();

        GetAgreementRequestRequest request =
                GetAgreementRequestRequest.builder()
                        .agreementRequestId(AGREEMENT_REQUEST_ID)
                        .build();

        GetAgreementRequestResponse response = marketplaceAgreementClient.getAgreementRequest(request);

        System.out.println("Agreement Request ID: " + response.agreementRequestId());
        System.out.println("Agreement Type: " + response.agreementType());
        System.out.println("Status: " + response.statusAsString());
        System.out.println("Approval Requirement: " + response.approvalRequirementAsString());
        if (response.agreementId() != null) {
            System.out.println("Agreement ID: " + response.agreementId());
        }
        System.out.println("Intent: " + response.intentAsString());
        System.out.println("Created At: " + response.createdAt());

        ChargeSummary chargeSummary = response.chargeSummary();
        System.out.println("Currency Code: " + chargeSummary.currencyCode());
        System.out.println("New Agreement Value: " + chargeSummary.newAgreementValue());
        // Tax fields are returned only when the request was created with tax estimation enabled.
        if (chargeSummary.estimatedTaxes() != null) {
            System.out.println("New Agreement Value After Tax: " + chargeSummary.newAgreementValueAfterTax());
            System.out.println("Estimated Taxes: " + chargeSummary.estimatedTaxes().totalAmount());
            System.out.println("Invoicing Entity: " + chargeSummary.invoicingEntity());
        }
        for (ExpectedCharge charge : chargeSummary.expectedCharges()) {
            System.out.println("Expected Charge ID: " + charge.id());
            System.out.println("  Amount: " + charge.amount());
            if (charge.amountAfterTax() != null) {
                System.out.println("  Amount After Tax: " + charge.amountAfterTax());
            }
            System.out.println("  Timing: " + charge.timingAsString());
            // Recurring charges of usage-based and recurring payment terms have no time.
            if (charge.time() != null) {
                System.out.println("  Time: " + charge.time());
            }
            if (charge.purchaseOrderReference() != null) {
                System.out.println("  Purchase Order Reference: " + charge.purchaseOrderReference());
            }
        }
        for (ItemizedCharge itemizedCharge : chargeSummary.itemizedCharges()) {
            System.out.println("Itemized Charge: " + itemizedCharge.dimensionKey() + ", quantity "
                    + itemizedCharge.oldQuantity() + " -> " + itemizedCharge.newQuantity() + ", amount "
                    + itemizedCharge.incrementalChargeAmount());
        }

        System.out.println("Proposer Account ID: " + response.proposer().accountId());
        System.out.println("Offer ID: " + response.proposalSummary().offerId());
        if (response.proposalSummary().offerSetId() != null) {
            System.out.println("Offer Set ID: " + response.proposalSummary().offerSetId());
        }
        for (Resource resource : response.proposalSummary().resources()) {
            System.out.println("Resource: " + resource.id() + " (" + resource.type() + ")");
        }
    }
}
