// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
const {
    MarketplaceAgreementClient,
    RejectAgreementApprovalCommand,
} = require("@aws-sdk/client-marketplace-agreement");

// Rejects an agreement approval as the administrator of the buyer's AWS Organization. The agreement request
// is rejected and no agreement is created.
const AGREEMENT_APPROVAL_ID = "<AGREEMENT APPROVAL ID HERE>";
const NOTE = "<REJECTION REASON HERE>";

async function rejectAgreementApproval() {
    const client = new MarketplaceAgreementClient();

    await client.send(
        new RejectAgreementApprovalCommand({
            buyerAgreementApprovalRejectionInput: {
                agreementApprovalId: AGREEMENT_APPROVAL_ID,
                note: NOTE,
            },
        })
    );

    console.log("Rejected Agreement Approval ID: " + AGREEMENT_APPROVAL_ID);
}

rejectAgreementApproval();
