// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi.buyer.agreementRequest;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.CancelAgreementRequestRequest;

// Cancels an agreement request that is pending approval, and its approval.
public class CancelAgreementRequest {

    private static final String AGREEMENT_REQUEST_ID = "<AGREEMENT REQUEST ID HERE>";

    public static void main(String[] args) {
        cancelAgreementRequest();
    }

    private static void cancelAgreementRequest() {
        MarketplaceAgreementClient marketplaceAgreementClient =
                MarketplaceAgreementClient.builder()
                        .httpClient(ApacheHttpClient.builder().build())
                        .credentialsProvider(ProfileCredentialsProvider.create())
                        .build();

        CancelAgreementRequestRequest request =
                CancelAgreementRequestRequest.builder()
                        .agreementRequestId(AGREEMENT_REQUEST_ID)
                        .build();

        marketplaceAgreementClient.cancelAgreementRequest(request);

        System.out.println("Cancelled Agreement Request ID: " + AGREEMENT_REQUEST_ID);
    }
}
