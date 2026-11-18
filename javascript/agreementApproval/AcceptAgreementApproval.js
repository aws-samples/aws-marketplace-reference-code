// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
const {
    MarketplaceAgreementClient,
    AcceptAgreementApprovalCommand,
} = require("@aws-sdk/client-marketplace-agreement");

// Approves an agreement approval as the administrator of the buyer's AWS Organization. When the approval
// is approved, the agreement request is accepted and the agreement is created; GetAgreementRequest returns its
// agreementId.
const AGREEMENT_APPROVAL_ID = "<AGREEMENT APPROVAL ID HERE>";
const NOTE = "<APPROVAL NOTE HERE>";

async function acceptAgreementApproval() {
    const client = new MarketplaceAgreementClient();

    await client.send(
        new AcceptAgreementApprovalCommand({
            buyerAgreementApprovalApproverInput: {
                agreementApprovalId: AGREEMENT_APPROVAL_ID,
                note: NOTE,
            },
        })
    );

    console.log("Approved Agreement Approval ID: " + AGREEMENT_APPROVAL_ID);
}

acceptAgreementApproval();
