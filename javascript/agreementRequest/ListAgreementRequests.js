// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
const {
    MarketplaceAgreementClient,
    ListAgreementRequestsCommand,
} = require("@aws-sdk/client-marketplace-agreement");

const STATUS = "PENDING_APPROVAL";

async function listAgreementRequests() {
    const client = new MarketplaceAgreementClient();

    let nextToken = null;

    do {
        const response = await client.send(
            new ListAgreementRequestsCommand({
                status: STATUS,
                nextToken: nextToken,
            })
        );

        for (const summary of response.items ?? []) {
            console.log("Agreement Request ID: " + summary.agreementRequestId);
            console.log("Agreement Type: " + summary.agreementType);
            console.log("Status: " + summary.status);
            if (summary.agreementId) {
                console.log("Agreement ID: " + summary.agreementId);
            }
            console.log("Offer ID: " + summary.proposalSummary.offerId);
            if (summary.proposalSummary.offerSetId !== undefined) {
                console.log("Offer Set ID: " + summary.proposalSummary.offerSetId);
            }
            for (const resource of summary.proposalSummary.resources ?? []) {
                console.log("Resource: " + resource.id + " (" + resource.type + ")");
            }
            console.log("---");
        }

        nextToken = response.nextToken;
    } while (nextToken != null);
}

listAgreementRequests();
