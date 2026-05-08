// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi.buyer.agreementCancellation;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AgreementCancellationRequestSummary;
import software.amazon.awssdk.services.marketplaceagreement.model.ListAgreementCancellationRequestsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.ListAgreementCancellationRequestsResponse;

public class ListAgreementCancellationRequests {

    private static final String PARTY_TYPE = "Proposer";

    public static void main(String[] args) {
        listAgreementCancellationRequests();
    }

    private static void listAgreementCancellationRequests() {
        MarketplaceAgreementClient marketplaceAgreementClient =
                MarketplaceAgreementClient.builder()
                        .httpClient(ApacheHttpClient.builder().build())
                        .credentialsProvider(ProfileCredentialsProvider.create())
                        .build();

        String nextToken = null;

        do {
            ListAgreementCancellationRequestsRequest request =
                    ListAgreementCancellationRequestsRequest.builder()
                            .partyType(PARTY_TYPE)
                            .nextToken(nextToken)
                            .build();

            ListAgreementCancellationRequestsResponse response =
                    marketplaceAgreementClient.listAgreementCancellationRequests(request);

            for (AgreementCancellationRequestSummary summary : response.items()) {
                System.out.println("Cancellation Request ID: " + summary.agreementCancellationRequestId());
                System.out.println("Agreement ID: " + summary.agreementId());
                System.out.println("Status: " + summary.statusAsString());
                System.out.println("Reason Code: " + summary.reasonCodeAsString());
                System.out.println("Agreement Type: " + summary.agreementType());
                System.out.println("Catalog: " + summary.catalog());
                System.out.println("Created At: " + summary.createdAt());
                System.out.println("Updated At: " + summary.updatedAt());
                System.out.println("---");
            }

            nextToken = response.nextToken();
        } while (nextToken != null);
    }
}
