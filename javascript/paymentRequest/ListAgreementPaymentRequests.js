const {
    MarketplaceAgreementClient,
    ListAgreementPaymentRequestsCommand,
} = require("@aws-sdk/client-marketplace-agreement");

const PARTY_TYPE = "Proposer";

async function listAgreementPaymentRequests() {
    const client = new MarketplaceAgreementClient();

    let nextToken = null;

    do {
        const response = await client.send(
            new ListAgreementPaymentRequestsCommand({
                partyType: PARTY_TYPE,
                nextToken: nextToken,
            })
        );

        for (const summary of response.items) {
            console.log("Payment Request ID: " + summary.paymentRequestId);
            console.log("Agreement ID: " + summary.agreementId);
            console.log("Status: " + summary.status);
            console.log("Name: " + summary.name);
            console.log("Charge ID: " + summary.chargeId);
            console.log("Charge Amount: " + summary.chargeAmount);
            console.log("Currency Code: " + summary.currencyCode);
            console.log("Created At: " + summary.createdAt);
            console.log("Updated At: " + summary.updatedAt);
            console.log("---");
        }

        nextToken = response.nextToken;
    } while (nextToken != null);
}

listAgreementPaymentRequests();
