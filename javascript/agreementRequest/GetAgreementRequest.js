// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
const {
    MarketplaceAgreementClient,
    GetAgreementRequestCommand,
} = require("@aws-sdk/client-marketplace-agreement");

const AGREEMENT_REQUEST_ID = "<AGREEMENT REQUEST ID HERE>";

async function getAgreementRequest() {
    const client = new MarketplaceAgreementClient();

    const response = await client.send(
        new GetAgreementRequestCommand({
            agreementRequestId: AGREEMENT_REQUEST_ID,
        })
    );

    console.log("Agreement Request ID: " + response.agreementRequestId);
    console.log("Agreement Type: " + response.agreementType);
    console.log("Status: " + response.status);
    console.log("Approval Requirement: " + response.approvalRequirement);
    if (response.agreementId !== undefined) {
        console.log("Agreement ID: " + response.agreementId);
    }
    console.log("Intent: " + response.intent);
    console.log("Created At: " + response.createdAt);

    const chargeSummary = response.chargeSummary;
    console.log("Currency Code: " + chargeSummary.currencyCode);
    console.log("New Agreement Value: " + chargeSummary.newAgreementValue);
    // Tax fields are returned only when the request was created with tax estimation enabled.
    if (chargeSummary.estimatedTaxes !== undefined) {
        console.log("New Agreement Value After Tax: " + chargeSummary.newAgreementValueAfterTax);
        console.log("Estimated Taxes: " + chargeSummary.estimatedTaxes.totalAmount);
        console.log("Invoicing Entity: " + JSON.stringify(chargeSummary.invoicingEntity));
    }
    for (const charge of chargeSummary.expectedCharges ?? []) {
        console.log("Expected Charge ID: " + charge.id);
        console.log("  Amount: " + charge.amount);
        if (charge.amountAfterTax !== undefined) {
            console.log("  Amount After Tax: " + charge.amountAfterTax);
        }
        console.log("  Timing: " + charge.timing);
        // Recurring charges of usage-based and recurring payment terms have no time.
        if (charge.time !== undefined) {
            console.log("  Time: " + charge.time);
        }
        if (charge.purchaseOrderReference !== undefined) {
            console.log("  Purchase Order Reference: " + charge.purchaseOrderReference);
        }
    }
    for (const itemizedCharge of chargeSummary.itemizedCharges ?? []) {
        console.log("Itemized Charge: " + itemizedCharge.dimensionKey + ", quantity "
            + itemizedCharge.oldQuantity + " -> " + itemizedCharge.newQuantity + ", amount "
            + itemizedCharge.incrementalChargeAmount);
    }

    console.log("Proposer Account ID: " + response.proposer.accountId);
    console.log("Offer ID: " + response.proposalSummary.offerId);
    if (response.proposalSummary.offerSetId !== undefined) {
        console.log("Offer Set ID: " + response.proposalSummary.offerSetId);
    }
    for (const resource of response.proposalSummary.resources ?? []) {
        console.log("Resource: " + resource.id + " (" + resource.type + ")");
    }
}

getAgreementRequest();
