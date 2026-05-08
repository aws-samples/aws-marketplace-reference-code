const { GetAgreementEntitlementsCommand } = require("@aws-sdk/client-marketplace-agreement");
const { randomUUID } = require("crypto");

function formatOutput(result) {
    console.log(JSON.stringify(result, null, 2));
}

function generateClientToken() {
    return randomUUID();
}

async function pollUntilEntitlementsAvailable(client, agreementId) {
    const timeout = 15 * 60 * 1000; // 15 minutes
    const initialBackoff = 2000; // 2 seconds
    const maxBackoff = 60000; // 60 seconds

    const deadline = Date.now() + timeout;
    let currentBackoff = initialBackoff;

    while (true) {
        const entitlementsResponse = await client.send(
            new GetAgreementEntitlementsCommand({ agreementId })
        );
        const allEntitlementsActive = entitlementsResponse.agreementEntitlements.every(
            (entitlement) => entitlement.status !== "PENDING"
        );
        if (allEntitlementsActive) {
            return entitlementsResponse;
        }
        if (Date.now() + currentBackoff > deadline) {
            throw new Error(
                "Entitlements still pending after 15 minutes for agreementId: " + agreementId
            );
        }
        console.log(`Entitlements not yet active. Retrying in ${currentBackoff / 1000} seconds...`);
        await new Promise((resolve) => setTimeout(resolve, currentBackoff));
        currentBackoff = Math.min(currentBackoff * 2, maxBackoff);
    }
}

module.exports = { formatOutput, generateClientToken, pollUntilEntitlementsAvailable };
