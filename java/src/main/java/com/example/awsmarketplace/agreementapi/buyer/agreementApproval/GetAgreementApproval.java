// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi.buyer.agreementApproval;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AgreementApprovalResource;
import software.amazon.awssdk.services.marketplaceagreement.model.ApproverOutcome;
import software.amazon.awssdk.services.marketplaceagreement.model.BuyerAgreementApproval;
import software.amazon.awssdk.services.marketplaceagreement.model.BuyerAgreementApprovalGroup;
import software.amazon.awssdk.services.marketplaceagreement.model.BuyerAgreementApprovalLevel;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementApprovalRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementApprovalResponse;

public class GetAgreementApproval {

    private static final String AGREEMENT_APPROVAL_ID = "<AGREEMENT APPROVAL ID HERE>";

    public static void main(String[] args) {
        getAgreementApproval();
    }

    private static void getAgreementApproval() {
        MarketplaceAgreementClient marketplaceAgreementClient =
                MarketplaceAgreementClient.builder()
                        .httpClient(ApacheHttpClient.builder().build())
                        .credentialsProvider(ProfileCredentialsProvider.create())
                        .build();

        GetAgreementApprovalRequest request =
                GetAgreementApprovalRequest.builder()
                        .agreementApprovalId(AGREEMENT_APPROVAL_ID)
                        .build();

        GetAgreementApprovalResponse response = marketplaceAgreementClient.getAgreementApproval(request);
        BuyerAgreementApproval approval = response.buyerAgreementApproval();

        System.out.println("Approval Type: " + approval.approvalTypeAsString());
        System.out.println("Agreement Approval ID: " + approval.agreementApprovalId());
        System.out.println("Agreement Request ID: " + approval.agreementRequestId());
        System.out.println("Name: " + approval.name());
        System.out.println("Status: " + approval.statusAsString());
        System.out.println("Requester Account ID: " + approval.requester().accountId());
        System.out.println("Proposer: " + approval.proposer().legalName() + " (" + approval.proposer().accountId() + ")");
        System.out.println("Offer ID: " + approval.proposalSummary().offerId());
        if (approval.proposalSummary().offerSetId() != null) {
            System.out.println("Offer Set ID: " + approval.proposalSummary().offerSetId());
        }
        System.out.println("Visibility Scope: " + approval.proposalSummary().visibilityScopeAsString());
        for (AgreementApprovalResource resource : approval.proposalSummary().resources()) {
            System.out.println("Resource: " + resource.name() + " (" + resource.id() + ", " + resource.type() + ")");
        }
        System.out.println("Plan Reference: " + approval.planInput().planReference());
        if (approval.planInput().requesterNote() != null) {
            System.out.println("Requester Note: " + approval.planInput().requesterNote());
        }
        System.out.println("Created At: " + approval.createdAt());
        System.out.println("Updated At: " + approval.updatedAt());
        System.out.println("Started At: " + approval.startedAt());
        System.out.println("Expires At: " + approval.expiresAt());
        System.out.println("Approval Needed By: " + approval.approvalNeededBy());
        for (BuyerAgreementApprovalLevel level : approval.levels()) {
            System.out.println("  Level: " + level.name());
            for (BuyerAgreementApprovalGroup group : level.groups()) {
                System.out.println("    Required Approvals: " + group.approvalCriteria().requiredApprovalCount());
                for (ApproverOutcome outcome : group.approvers()) {
                    printApproverOutcome(outcome);
                }
            }
        }
    }

    private static void printApproverOutcome(ApproverOutcome outcome) {
        switch (outcome.type()) {
            case AWS_ORGANIZATION_APPROVER_OUTCOME:
                System.out.println("    Organization admin: " + outcome.awsOrganizationApproverOutcome().statusAsString()
                        + ", approverOutcomeId " + outcome.awsOrganizationApproverOutcome().approverOutcomeId());
                break;
            case EMAIL_APPROVER_OUTCOME:
                System.out.println("    Email approver " + outcome.emailApproverOutcome().emailAddress() + ": "
                        + outcome.emailApproverOutcome().statusAsString()
                        + ", approverOutcomeId " + outcome.emailApproverOutcome().approverOutcomeId());
                break;
            case PROCUREMENT_TOOL_APPROVER_OUTCOME:
                System.out.println("    Procurement tool " + outcome.procurementToolApproverOutcome().name() + ": "
                        + outcome.procurementToolApproverOutcome().statusAsString()
                        + ", approverOutcomeId " + outcome.procurementToolApproverOutcome().approverOutcomeId());
                break;
            default:
                System.out.println("    Approver: " + outcome);
        }
    }
}
