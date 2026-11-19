// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
const {
    MarketplaceAgreementClient,
    paginateGetAgreementRequestApprovalPlans,
} = require("@aws-sdk/client-marketplace-agreement");

const AGREEMENT_REQUEST_ID = "<AGREEMENT REQUEST ID HERE>";

async function getAgreementRequestApprovalPlans() {
    const client = new MarketplaceAgreementClient();

    for await (const page of paginateGetAgreementRequestApprovalPlans(
        { client },
        { agreementRequestId: AGREEMENT_REQUEST_ID }
    )) {
        for (const item of page.items) {
            const plan = item.buyerAgreementApprovalPlan;
            console.log("Plan Reference: " + plan.planReference);
            console.log("Plan Name: " + plan.name);
            for (const level of plan.levels) {
                console.log("  Level: " + level.name);
                for (const group of level.groups) {
                    console.log("    Required Approvals: " + group.approvalCriteria.requiredApprovalCount);
                    for (const approver of group.approvers) {
                        console.log("    Approver: " + JSON.stringify(approver));
                    }
                }
            }
            console.log("---");
        }
    }
}

getAgreementRequestApprovalPlans();
