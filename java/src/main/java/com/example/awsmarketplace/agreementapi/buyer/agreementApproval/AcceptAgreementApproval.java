// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi.buyer.agreementApproval;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptAgreementApprovalRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.BuyerAgreementApprovalApproverInput;

// Approves an agreement approval as the administrator of the buyer's AWS Organization. When the approval
// is approved, the agreement request is accepted and the agreement is created; GetAgreementRequest returns its
// agreementId.
public class AcceptAgreementApproval {

    private static final String AGREEMENT_APPROVAL_ID = "<AGREEMENT APPROVAL ID HERE>";
    private static final String NOTE = "<APPROVAL NOTE HERE>";

    public static void main(String[] args) {
        acceptAgreementApproval();
    }

    private static void acceptAgreementApproval() {
        MarketplaceAgreementClient marketplaceAgreementClient =
                MarketplaceAgreementClient.builder()
                        .httpClient(ApacheHttpClient.builder().build())
                        .credentialsProvider(ProfileCredentialsProvider.create())
                        .build();

        AcceptAgreementApprovalRequest request =
                AcceptAgreementApprovalRequest.builder()
                        .buyerAgreementApprovalApproverInput(BuyerAgreementApprovalApproverInput.builder()
                                .agreementApprovalId(AGREEMENT_APPROVAL_ID)
                                .note(NOTE)
                                .build())
                        .build();

        marketplaceAgreementClient.acceptAgreementApproval(request);

        System.out.println("Approved Agreement Approval ID: " + AGREEMENT_APPROVAL_ID);
    }
}
