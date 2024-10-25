// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.amazon.samplelib;

import static org.junit.Assert.assertEquals;

import java.io.IOException;

import org.junit.Test;

import com.example.awsmarketplace.catalogapi.RunChangesets;

import software.amazon.awssdk.services.marketplacecatalog.model.StartChangeSetResponse;

public class CatalogAPIRunChangesetsTest {
	@Test
    public void testRunChangesets() {
		// Ideally, store all testing changesets with real ids for testing in S3 bucket. 
		// Categorize changesets with different purpose
		// offers, products, resaleauthorization, etc. Then run them all here.
		// String changeSetsInput = Helpers.getJsonStringFromS3Bucket(bucketName, fiieKey)
		String inputChangeSetFile = "changeSets/offers/CreateReplacementOfferFromAGWithContractPricingDetailDocument.json";
		String changeSetsInput = RunChangesets.readChangeSetToString(inputChangeSetFile);
		StartChangeSetResponse result;
		try {
			result = RunChangesets.getChangeSetRequestResult(changeSetsInput);
			assertEquals(result.sdkHttpResponse().statusCode(), 200);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}