// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi.buyer.agreementRequest;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AgreementRequestSummary;
import software.amazon.awssdk.services.marketplaceagreement.model.ListAgreementRequestsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.ListAgreementRequestsResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.Resource;

public class ListAgreementRequests {

    private static final String STATUS = "PENDING_APPROVAL";

    public static void main(String[] args) {
        listAgreementRequests();
    }

    private static void listAgreementRequests() {
        MarketplaceAgreementClient marketplaceAgreementClient =
                MarketplaceAgreementClient.builder()
                        .httpClient(ApacheHttpClient.builder().build())
                        .credentialsProvider(ProfileCredentialsProvider.create())
                        .build();

        String nextToken = null;

        do {
            ListAgreementRequestsRequest request =
                    ListAgreementRequestsRequest.builder()
                            .status(STATUS)
                            .nextToken(nextToken)
                            .build();

            ListAgreementRequestsResponse response = marketplaceAgreementClient.listAgreementRequests(request);

            for (AgreementRequestSummary summary : response.items()) {
                System.out.println("Agreement Request ID: " + summary.agreementRequestId());
                System.out.println("Agreement Type: " + summary.agreementType());
                System.out.println("Status: " + summary.statusAsString());
                if (summary.agreementId() != null) {
                    System.out.println("Agreement ID: " + summary.agreementId());
                }
                System.out.println("Offer ID: " + summary.proposalSummary().offerId());
                if (summary.proposalSummary().offerSetId() != null) {
                    System.out.println("Offer Set ID: " + summary.proposalSummary().offerSetId());
                }
                for (Resource resource : summary.proposalSummary().resources()) {
                    System.out.println("Resource: " + resource.id() + " (" + resource.type() + ")");
                }
                System.out.println("---");
            }

            nextToken = response.nextToken();
        } while (nextToken != null);
    }
}
