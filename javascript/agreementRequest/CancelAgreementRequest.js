// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
const {
    MarketplaceAgreementClient,
    CancelAgreementRequestCommand,
} = require("@aws-sdk/client-marketplace-agreement");

// Cancels an agreement request that is pending approval, and its approval.
const AGREEMENT_REQUEST_ID = "<AGREEMENT REQUEST ID HERE>";

async function cancelAgreementRequest() {
    const client = new MarketplaceAgreementClient();

    await client.send(
        new CancelAgreementRequestCommand({
            agreementRequestId: AGREEMENT_REQUEST_ID,
        })
    );

    console.log("Cancelled Agreement Request ID: " + AGREEMENT_REQUEST_ID);
}

cancelAgreementRequest();
