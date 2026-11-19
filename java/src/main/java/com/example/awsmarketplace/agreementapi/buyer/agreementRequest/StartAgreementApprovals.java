// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi.buyer.agreementRequest;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AgreementApprovalPlanInput;
import software.amazon.awssdk.services.marketplaceagreement.model.AgreementApprovalPurchaseOrder;
import software.amazon.awssdk.services.marketplaceagreement.model.AgreementApprovalSummary;
import software.amazon.awssdk.services.marketplaceagreement.model.BuyerAgreementApprovalPlanInput;
import software.amazon.awssdk.services.marketplaceagreement.model.StartAgreementApprovalsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.StartAgreementApprovalsResponse;

public class StartAgreementApprovals {

    private static final String AGREEMENT_REQUEST_ID = "<AGREEMENT REQUEST ID HERE>";
    // planReference of a plan returned by GetAgreementRequestApprovalPlans for this agreement request.
    private static final String PLAN_REFERENCE = "<PLAN REFERENCE HERE>";
    private static final String REQUESTER_NOTE = "<NOTE FOR THE APPROVERS HERE>";
    // Optional: a purchase order for an expected charge, by its id from GetAgreementRequest chargeSummary.
    private static final String CHARGE_ID = null;
    private static final String PURCHASE_ORDER_REFERENCE = "<PURCHASE ORDER REFERENCE HERE>";

    public static void main(String[] args) {
        startAgreementApprovals();
    }

    private static void startAgreementApprovals() {
        MarketplaceAgreementClient marketplaceAgreementClient =
                MarketplaceAgreementClient.builder()
                        .httpClient(ApacheHttpClient.builder().build())
                        .credentialsProvider(ProfileCredentialsProvider.create())
                        .build();

        StartAgreementApprovalsRequest.Builder requestBuilder =
                StartAgreementApprovalsRequest.builder()
                        .agreementRequestId(AGREEMENT_REQUEST_ID)
                        .planInputs(AgreementApprovalPlanInput.fromBuyerAgreementApprovalPlanInput(
                                BuyerAgreementApprovalPlanInput.builder()
                                        .planReference(PLAN_REFERENCE)
                                        .requesterNote(REQUESTER_NOTE)
                                        .build()));
        if (CHARGE_ID != null) {
            requestBuilder.purchaseOrders(AgreementApprovalPurchaseOrder.builder()
                    .chargeId(CHARGE_ID)
                    .purchaseOrderReference(PURCHASE_ORDER_REFERENCE)
                    .build());
        }
        StartAgreementApprovalsRequest request = requestBuilder.build();

        StartAgreementApprovalsResponse response = marketplaceAgreementClient.startAgreementApprovals(request);

        for (AgreementApprovalSummary summary : response.approvalSummaries()) {
            System.out.println("Approval Type: " + summary.approvalTypeAsString());
            System.out.println("Agreement Request ID: " + summary.agreementRequestId());
            System.out.println("Agreement Approval ID: " + summary.agreementApprovalId());
            System.out.println("Name: " + summary.name());
            System.out.println("Status: " + summary.statusAsString());
            System.out.println("Created At: " + summary.createdAt());
            System.out.println("Updated At: " + summary.updatedAt());
            System.out.println("Started At: " + summary.startedAt());
            System.out.println("Expires At: " + summary.expiresAt());
            System.out.println("Approval Needed By: " + summary.approvalNeededBy());
            System.out.println("---");
        }
    }
}
