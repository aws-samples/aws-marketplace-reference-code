// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.catalogapi;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.*;
import com.example.awsmarketplace.utils.ReferenceCodesUtils;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplacecatalog.MarketplaceCatalogClient;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeChangeSetRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeChangeSetResponse;

public class DescribeChangeSet {

	/*
	 * Describe a changeset
	 */
	public static void main(String[] args) {
		
		String changesetId = args.length > 0 ? args[0] : CHANGESET_ID;

		DescribeChangeSetResponse describeChangeSetResponse = getDescribeChangeSetResponse(changesetId);

		ReferenceCodesUtils.formatOutput(describeChangeSetResponse);
		
	}

	public static DescribeChangeSetResponse getDescribeChangeSetResponse(String changesetId) {

		MarketplaceCatalogClient marketplaceCatalogClient = 
				MarketplaceCatalogClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();

		DescribeChangeSetRequest describeChangeSetRequest = 
				DescribeChangeSetRequest.builder()
				.catalog(AWS_MP_CATALOG)
				.changeSetId(changesetId)
				.build();

		DescribeChangeSetResponse describeChangeSetResponse = marketplaceCatalogClient.describeChangeSet(describeChangeSetRequest);
		return describeChangeSetResponse;
	}
		
}
