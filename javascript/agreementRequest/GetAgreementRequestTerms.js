// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
const {
    MarketplaceAgreementClient,
    paginateGetAgreementRequestTerms,
} = require("@aws-sdk/client-marketplace-agreement");

const AGREEMENT_REQUEST_ID = "<AGREEMENT REQUEST ID HERE>";

async function getAgreementRequestTerms() {
    const client = new MarketplaceAgreementClient();

    for await (const page of paginateGetAgreementRequestTerms(
        { client },
        { agreementRequestId: AGREEMENT_REQUEST_ID }
    )) {
        for (const term of page.terms) {
            const [termType, termValue] = Object.entries(term)[0];
            console.log("Term Type: " + termType);
            console.log(JSON.stringify(termValue, null, 2));
            console.log("---");
        }
    }
}

getAgreementRequestTerms();
