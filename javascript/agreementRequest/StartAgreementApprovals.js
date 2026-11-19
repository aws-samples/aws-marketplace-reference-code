// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
const {
    MarketplaceAgreementClient,
    StartAgreementApprovalsCommand,
} = require("@aws-sdk/client-marketplace-agreement");

const AGREEMENT_REQUEST_ID = "<AGREEMENT REQUEST ID HERE>";
// planReference of a plan returned by GetAgreementRequestApprovalPlans for this agreement request.
const PLAN_REFERENCE = "<PLAN REFERENCE HERE>";
const REQUESTER_NOTE = "<NOTE FOR THE APPROVERS HERE>";
// Optional: a purchase order for an expected charge, by its id from GetAgreementRequest chargeSummary.
const CHARGE_ID = undefined;
const PURCHASE_ORDER_REFERENCE = "<PURCHASE ORDER REFERENCE HERE>";

async function startAgreementApprovals() {
    const client = new MarketplaceAgreementClient();

    const response = await client.send(
        new StartAgreementApprovalsCommand({
            agreementRequestId: AGREEMENT_REQUEST_ID,
            planInputs: [
                {
                    buyerAgreementApprovalPlanInput: {
                        planReference: PLAN_REFERENCE,
                        requesterNote: REQUESTER_NOTE,
                    },
                },
            ],
            purchaseOrders: CHARGE_ID
                ? [{ chargeId: CHARGE_ID, purchaseOrderReference: PURCHASE_ORDER_REFERENCE }]
                : undefined,
        })
    );

    for (const summary of response.approvalSummaries) {
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
}

startAgreementApprovals();
