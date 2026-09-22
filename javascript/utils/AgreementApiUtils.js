// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
const {
    DescribeAgreementCommand,
    GetAgreementEntitlementsCommand,
    GetAgreementTermsCommand,
} = require("@aws-sdk/client-marketplace-agreement");
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

/**
 * Prints the renewal term that the proposer set on the offer.
 */
async function printRenewalTerm(client, agreementId) {
    let nextToken = undefined;

    do {
        const response = await client.send(
            new GetAgreementTermsCommand({ agreementId, nextToken })
        );

        for (const acceptedTerm of response.acceptedTerms ?? []) {
            if (!acceptedTerm.renewalTerm) {
                continue;
            }
            const renewalTerm = acceptedTerm.renewalTerm;

            console.log("Renewal Term ID: " + renewalTerm.id);

            if (renewalTerm.configuration) {
                console.log("Auto Renew Enabled: " + renewalTerm.configuration.enableAutoRenew);
            }

            if (renewalTerm.lockoutPeriod !== undefined) {
                console.log("Lockout Period: " + renewalTerm.lockoutPeriod);
            }

            if (renewalTerm.maxRenewals !== undefined) {
                console.log("Max Renewals: " + renewalTerm.maxRenewals);
            }

            if (renewalTerm.adjustmentDeadline !== undefined) {
                console.log("Adjustment Deadline: " + renewalTerm.adjustmentDeadline);
            }

            printPriceIncrease(renewalTerm.priceIncrease);

            for (const termTemplate of renewalTerm.termTemplates ?? []) {
                printTermTemplate(termTemplate);
            }
        }

        nextToken = response.nextToken;
    } while (nextToken);
}

/**
 * Prints the price increase that is applied each time the agreement renews.
 */
function printPriceIncrease(priceIncrease) {
    if (!priceIncrease) {
        console.log("Price Increase: none (no uplift is set, so the agreement renews at the same price)");
        return;
    }

    if (priceIncrease.fixedPercentage) {
        const fixedPercentage = priceIncrease.fixedPercentage.value;
        if (Number(fixedPercentage) === 0) {
            console.log("Fixed Price Increase Percentage: " + fixedPercentage
                        + " (the agreement renews at the same price)");
        } else {
            console.log("Fixed Price Increase Percentage: " + fixedPercentage);
        }
    } else if (priceIncrease.percentageRange) {
        console.log("Price Increase Min Percentage: " + priceIncrease.percentageRange.minValue);
        console.log("Price Increase Max Percentage: " + priceIncrease.percentageRange.maxValue);
        console.log("Price Increase Default Percentage: " + priceIncrease.percentageRange.defaultValue);
    }
}

/**
 * termTemplate is a union. Payment schedules are the only variant the renewal term supports
 * today, so any other variant is skipped rather than printed.
 */
function printTermTemplate(termTemplate) {
    if (!termTemplate.paymentScheduleTermTemplate) {
        return;
    }

    console.log("Payment Schedule Template:");
    for (const entry of termTemplate.paymentScheduleTermTemplate.schedule ?? []) {
        let line = "  Charge Date Offset: " + entry.chargeDateOffset
                   + ", Charge Percentage: " + entry.chargePercentage;

        if (entry.dayOfMonth !== undefined) {
            line += ", Day Of Month: " + entry.dayOfMonth;
        }

        console.log(line);
    }
}

/**
 * Prints the end time behavior of an agreement.
 */
async function printEndTimeBehavior(client, agreementId, label) {
    const describeAgreementResponse = await client.send(
        new DescribeAgreementCommand({ agreementId })
    );

    const endTimeBehavior = describeAgreementResponse.endTimeBehavior;
    if (!endTimeBehavior) {
        console.log(label + " - End Time Behavior: none (this agreement has no end date)");
        return;
    }

    console.log(label + " - End Time Behavior Type: " + endTimeBehavior.type);

    if (endTimeBehavior.reasonCode) {
        console.log(label + " - End Time Behavior Reason Code: " + endTimeBehavior.reasonCode);
    }

    if (endTimeBehavior.renewalSummary && endTimeBehavior.renewalSummary.offerId) {
        console.log(label + " - Renewal Offer ID: " + endTimeBehavior.renewalSummary.offerId);
    }
}

module.exports = {
    formatOutput,
    generateClientToken,
    pollUntilEntitlementsAvailable,
    printRenewalTerm,
    printEndTimeBehavior,
};
