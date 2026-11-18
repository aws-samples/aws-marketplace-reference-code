// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi.buyer.agreementApproval;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AgreementApprovalSummary;
import software.amazon.awssdk.services.marketplaceagreement.model.ListAgreementApprovalsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.ListAgreementApprovalsResponse;

public class ListAgreementApprovals {

    // REQUESTER lists the approvals the caller started. AWS_ORGANIZATION_ADMIN lists the approvals the caller
    // decides as the administrator of its AWS Organization.
    private static final String PARTY_TYPE = "AWS_ORGANIZATION_ADMIN";
    private static final String STATUS = "PENDING_APPROVAL";

    public static void main(String[] args) {
        listAgreementApprovals();
    }

    private static void listAgreementApprovals() {
        MarketplaceAgreementClient marketplaceAgreementClient =
                MarketplaceAgreementClient.builder()
                        .httpClient(ApacheHttpClient.builder().build())
                        .credentialsProvider(ProfileCredentialsProvider.create())
                        .build();

        String nextToken = null;

        do {
            ListAgreementApprovalsRequest request =
                    ListAgreementApprovalsRequest.builder()
                            .partyType(PARTY_TYPE)
                            .status(STATUS)
                            .nextToken(nextToken)
                            .build();

            ListAgreementApprovalsResponse response = marketplaceAgreementClient.listAgreementApprovals(request);

            for (AgreementApprovalSummary summary : response.items()) {
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

            nextToken = response.nextToken();
        } while (nextToken != null);
    }
}
