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

		MarketplaceCatalogClient marketplaceCatalogClient = 
				MarketplaceCatalogClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();
		
		DescribeEntityRequest describeEntityRequest = 
				DescribeEntityRequest.builder()
				.catalog(AWS_MP_CATALOG)
				.entityId(OFFER_ID)
				.build();

		DescribeEntityResponse describeEntityResponse = marketplaceCatalogClient.describeEntity(describeEntityRequest);

		ReferenceCodesUtils.formatOutput(describeEntityResponse);
	}
}
