// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi.buyer.agreementRequest;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AgreementApprovalPlan;
import software.amazon.awssdk.services.marketplaceagreement.model.Approver;
import software.amazon.awssdk.services.marketplaceagreement.model.BuyerAgreementApprovalPlan;
import software.amazon.awssdk.services.marketplaceagreement.model.BuyerAgreementApprovalPlanGroup;
import software.amazon.awssdk.services.marketplaceagreement.model.BuyerAgreementApprovalPlanLevel;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementRequestApprovalPlansRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementRequestApprovalPlansResponse;

public class GetAgreementRequestApprovalPlans {

    private static final String AGREEMENT_REQUEST_ID = "<AGREEMENT REQUEST ID HERE>";

    public static void main(String[] args) {
        getAgreementRequestApprovalPlans();
    }

    private static void getAgreementRequestApprovalPlans() {
        MarketplaceAgreementClient marketplaceAgreementClient =
                MarketplaceAgreementClient.builder()
                        .httpClient(ApacheHttpClient.builder().build())
                        .credentialsProvider(ProfileCredentialsProvider.create())
                        .build();

        GetAgreementRequestApprovalPlansRequest request =
                GetAgreementRequestApprovalPlansRequest.builder()
                        .agreementRequestId(AGREEMENT_REQUEST_ID)
                        .build();

        for (GetAgreementRequestApprovalPlansResponse page :
                marketplaceAgreementClient.getAgreementRequestApprovalPlansPaginator(request)) {
            for (AgreementApprovalPlan item : page.items()) {
                BuyerAgreementApprovalPlan plan = item.buyerAgreementApprovalPlan();
                System.out.println("Plan Reference: " + plan.planReference());
                System.out.println("Plan Name: " + plan.name());
                for (BuyerAgreementApprovalPlanLevel level : plan.levels()) {
                    System.out.println("  Level: " + level.name());
                    for (BuyerAgreementApprovalPlanGroup group : level.groups()) {
                        System.out.println("    Required Approvals: " + group.approvalCriteria().requiredApprovalCount());
                        for (Approver approver : group.approvers()) {
                            System.out.println("    Approver: " + approver);
                        }
                    }
                }
                System.out.println("---");
            }
        }
    }
}
