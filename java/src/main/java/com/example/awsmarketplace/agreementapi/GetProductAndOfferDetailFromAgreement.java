﻿// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.Resource;

import java.util.ArrayList;
import java.util.List;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.*;
import com.example.awsmarketplace.utils.ReferenceCodesUtils;

import software.amazon.awssdk.services.marketplacecatalog.MarketplaceCatalogClient;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityResponse;

public class GetProductAndOfferDetailFromAgreement {

	public static void main(String[] args) {

		// call Agreement API to get offer and product information for the agreement
		
		String agreementId = args.length > 0 ? args[0] : AGREEMENT_ID;
		
		List<DescribeEntityResponse> entityResponseList = getEntities(agreementId);

		for (DescribeEntityResponse response : entityResponseList) {
			ReferenceCodesUtils.formatOutput(response);
		}
	}

	public static List<DescribeEntityResponse> getEntities(String agreementId) {
		List<DescribeEntityResponse> entityResponseList = new ArrayList<DescribeEntityResponse> ();
		
		MarketplaceAgreementClient marketplaceAgreementClient = 
				MarketplaceAgreementClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();

		DescribeAgreementRequest describeAgreementRequest = 
				DescribeAgreementRequest.builder()
				.agreementId(agreementId)
				.build();

		DescribeAgreementResponse describeAgreementResponse = marketplaceAgreementClient.describeAgreement(describeAgreementRequest);

		// get offer id for the given agreement

		String offerId = describeAgreementResponse.proposalSummary().offerId();

		// get all the product ids for this agreement
		
		List<String> productIds = new ArrayList<String>();
		for (Resource resource : describeAgreementResponse.proposalSummary().resources()) {
			productIds.add(resource.id());
		}

		// call Catalog API to get the details of the offer and products
		
		MarketplaceCatalogClient marketplaceCatalogClient = 
				MarketplaceCatalogClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();
		
		DescribeEntityRequest describeEntityRequest = 
				DescribeEntityRequest.builder()
				.catalog(AWS_MP_CATALOG)
				.entityId(offerId).build();

		DescribeEntityResponse describeEntityResponse = marketplaceCatalogClient.describeEntity(describeEntityRequest);
		
		entityResponseList.add(describeEntityResponse);

		for (String productId : productIds) {
			describeEntityRequest = 
					DescribeEntityRequest.builder()
					.catalog(AWS_MP_CATALOG)
					.entityId(productId).build();
			describeEntityResponse = marketplaceCatalogClient.describeEntity(describeEntityRequest);
			System.out.println("Print details for product " + productId);
			entityResponseList.add(describeEntityResponse);
		}
		return entityResponseList;
	}
}
