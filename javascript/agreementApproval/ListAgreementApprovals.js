// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
const {
    MarketplaceAgreementClient,
    ListAgreementApprovalsCommand,
} = require("@aws-sdk/client-marketplace-agreement");

// REQUESTER lists the approvals the caller started. AWS_ORGANIZATION_ADMIN lists the approvals the caller
// decides as the administrator of its AWS Organization.
const PARTY_TYPE = "AWS_ORGANIZATION_ADMIN";
const STATUS = "PENDING_APPROVAL";

async function listAgreementApprovals() {
    const client = new MarketplaceAgreementClient();

    let nextToken = null;

    do {
        const response = await client.send(
            new ListAgreementApprovalsCommand({
                partyType: PARTY_TYPE,
                status: STATUS,
                nextToken: nextToken,
            })
        );

        for (const summary of response.items) {
            console.log("Approval Type: " + summary.approvalType);
            console.log("Agreement Request ID: " + summary.agreementRequestId);
            console.log("Agreement Approval ID: " + summary.agreementApprovalId);
            console.log("Name: " + summary.name);
            console.log("Status: " + summary.status);
            console.log("Created At: " + summary.createdAt);
            console.log("Updated At: " + summary.updatedAt);
            console.log("Started At: " + summary.startedAt);
            console.log("Expires At: " + summary.expiresAt);
            console.log("Approval Needed By: " + summary.approvalNeededBy);
            console.log("---");
        }

        nextToken = response.nextToken;
    } while (nextToken != null);
}

listAgreementApprovals();
