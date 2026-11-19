// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi.buyer.agreementApproval;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.BuyerAgreementApprovalRejectionInput;
import software.amazon.awssdk.services.marketplaceagreement.model.RejectAgreementApprovalRequest;

// Rejects an agreement approval as the administrator of the buyer's AWS Organization. The agreement request
// is rejected and no agreement is created.
public class RejectAgreementApproval {

    private static final String AGREEMENT_APPROVAL_ID = "<AGREEMENT APPROVAL ID HERE>";
    private static final String NOTE = "<REJECTION REASON HERE>";

    public static void main(String[] args) {
        rejectAgreementApproval();
    }

    private static void rejectAgreementApproval() {
        MarketplaceAgreementClient marketplaceAgreementClient =
                MarketplaceAgreementClient.builder()
                        .httpClient(ApacheHttpClient.builder().build())
                        .credentialsProvider(ProfileCredentialsProvider.create())
                        .build();

        RejectAgreementApprovalRequest request =
                RejectAgreementApprovalRequest.builder()
                        .buyerAgreementApprovalRejectionInput(BuyerAgreementApprovalRejectionInput.builder()
                                .agreementApprovalId(AGREEMENT_APPROVAL_ID)
                                .note(NOTE)
                                .build())
                        .build();

        marketplaceAgreementClient.rejectAgreementApproval(request);

        System.out.println("Rejected Agreement Approval ID: " + AGREEMENT_APPROVAL_ID);
    }
}
