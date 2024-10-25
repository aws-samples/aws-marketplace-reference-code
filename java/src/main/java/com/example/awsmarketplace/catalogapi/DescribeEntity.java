﻿// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.catalogapi;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.*;
import com.example.awsmarketplace.utils.ReferenceCodesUtils;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplacecatalog.MarketplaceCatalogClient;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityResponse;

public class DescribeEntity {

	/*
	 * Describe my AMI or SaaS or Container product and check if it contains all the information I need to know about the product
	 */
	public static void main(String[] args) {

		String offerId = args.length > 0 ? args[0] : OFFER_ID;

		DescribeEntityResponse describeEntityResponse = getDescribeEntityResponse(offerId);

		ReferenceCodesUtils.formatOutput(describeEntityResponse);
	}

	public static DescribeEntityResponse getDescribeEntityResponse(String offerId) {
		MarketplaceCatalogClient marketplaceCatalogClient = 
				MarketplaceCatalogClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();
		
		DescribeEntityRequest describeEntityRequest = 
				DescribeEntityRequest.builder()
				.catalog(AWS_MP_CATALOG)
				.entityId(offerId)
				.build();

		DescribeEntityResponse describeEntityResponse = marketplaceCatalogClient.describeEntity(describeEntityRequest);
		return describeEntityResponse;
	}
}
