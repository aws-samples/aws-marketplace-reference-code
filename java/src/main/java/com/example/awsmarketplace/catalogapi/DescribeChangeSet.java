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

		MarketplaceCatalogClient marketplaceCatalogClient = 
				MarketplaceCatalogClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();

		DescribeChangeSetRequest describeChangeSetRequest = 
				DescribeChangeSetRequest.builder()
				.catalog(AWS_MP_CATALOG)
				.changeSetId(CHANGESET_ID)
				.build();

		DescribeChangeSetResponse describeChangeSetResponse = marketplaceCatalogClient.describeChangeSet(describeChangeSetRequest);

		ReferenceCodesUtils.formatOutput(describeChangeSetResponse);
		
	}
		
}
