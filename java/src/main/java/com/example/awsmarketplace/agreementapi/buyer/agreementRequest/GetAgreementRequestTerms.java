// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi.buyer.agreementRequest;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AgreementRequestTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementRequestTermsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementRequestTermsResponse;

public class GetAgreementRequestTerms {

    private static final String AGREEMENT_REQUEST_ID = "<AGREEMENT REQUEST ID HERE>";

    public static void main(String[] args) {
        getAgreementRequestTerms();
    }

    private static void getAgreementRequestTerms() {
        MarketplaceAgreementClient marketplaceAgreementClient =
                MarketplaceAgreementClient.builder()
                        .httpClient(ApacheHttpClient.builder().build())
                        .credentialsProvider(ProfileCredentialsProvider.create())
                        .build();

        GetAgreementRequestTermsRequest request =
                GetAgreementRequestTermsRequest.builder()
                        .agreementRequestId(AGREEMENT_REQUEST_ID)
                        .build();

        for (GetAgreementRequestTermsResponse page :
                marketplaceAgreementClient.getAgreementRequestTermsPaginator(request)) {
            for (AgreementRequestTerm term : page.terms()) {
                System.out.println("Term Type: " + term.type());
                System.out.println(term);
                System.out.println("---");
            }
        }
    }
}
