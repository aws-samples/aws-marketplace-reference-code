// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
const {
    MarketplaceAgreementClient,
    GetAgreementApprovalCommand,
} = require("@aws-sdk/client-marketplace-agreement");

const AGREEMENT_APPROVAL_ID = "<AGREEMENT APPROVAL ID HERE>";

async function getAgreementApproval() {
    const client = new MarketplaceAgreementClient();

    const response = await client.send(
        new GetAgreementApprovalCommand({
            agreementApprovalId: AGREEMENT_APPROVAL_ID,
        })
    );
    const approval = response.buyerAgreementApproval;

    console.log("Approval Type: " + approval.approvalType);
    console.log("Agreement Approval ID: " + approval.agreementApprovalId);
    console.log("Agreement Request ID: " + approval.agreementRequestId);
    console.log("Name: " + approval.name);
    console.log("Status: " + approval.status);
    console.log("Requester Account ID: " + approval.requester.accountId);
    console.log("Proposer: " + approval.proposer.legalName + " (" + approval.proposer.accountId + ")");
    console.log("Offer ID: " + approval.proposalSummary.offerId);
    if (approval.proposalSummary.offerSetId !== undefined) {
        console.log("Offer Set ID: " + approval.proposalSummary.offerSetId);
    }
    console.log("Visibility Scope: " + approval.proposalSummary.visibilityScope);
    for (const resource of approval.proposalSummary.resources ?? []) {
        console.log("Resource: " + resource.name + " (" + resource.id + ", " + resource.type + ")");
    }
    console.log("Plan Reference: " + approval.planInput.planReference);
    if (approval.planInput.requesterNote !== undefined) {
        console.log("Requester Note: " + approval.planInput.requesterNote);
    }
    console.log("Created At: " + approval.createdAt);
    console.log("Updated At: " + approval.updatedAt);
    console.log("Started At: " + approval.startedAt);
    console.log("Expires At: " + approval.expiresAt);
    console.log("Approval Needed By: " + approval.approvalNeededBy);
    for (const level of approval.levels) {
        console.log("  Level: " + level.name);
        for (const group of level.groups) {
            console.log("    Required Approvals: " + group.approvalCriteria.requiredApprovalCount);
            for (const outcome of group.approvers) {
                printApproverOutcome(outcome);
            }
        }
    }
}

function printApproverOutcome(outcome) {
    if (outcome.awsOrganizationApproverOutcome) {
        const admin = outcome.awsOrganizationApproverOutcome;
        console.log("    Organization admin: " + admin.status + ", approverOutcomeId " + admin.approverOutcomeId);
    } else if (outcome.emailApproverOutcome) {
        const email = outcome.emailApproverOutcome;
        console.log("    Email approver " + email.emailAddress + ": " + email.status
            + ", approverOutcomeId " + email.approverOutcomeId);
    } else if (outcome.procurementToolApproverOutcome) {
        const tool = outcome.procurementToolApproverOutcome;
        console.log("    Procurement tool " + tool.name + ": " + tool.status
            + ", approverOutcomeId " + tool.approverOutcomeId);
    } else {
        console.log("    Approver: " + JSON.stringify(outcome));
    }
}

getAgreementApproval();
