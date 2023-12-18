package com.example.awsmarketplace.catalogapi;

import java.util.ArrayList;
import java.util.List;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.*;
import com.example.awsmarketplace.utils.ReferenceCodesUtils;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.core.document.Document;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplacecatalog.MarketplaceCatalogClient;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityResponse;
import software.amazon.awssdk.services.marketplacecatalog.model.EntitySummary;
import software.amazon.awssdk.services.marketplacecatalog.model.ListEntitiesRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.ListEntitiesResponse;

public class ListAllCppoOffers {

	/*
	 * List all CPPOs created by a channel partner
	 */
	public static void main(String[] args) {
		
		MarketplaceCatalogClient marketplaceCatalogClient = 
				MarketplaceCatalogClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();
		
		// get all offer entity ids
		List<String> entityIdList = new ArrayList<String>();

		ListEntitiesRequest listEntitiesRequest = 
				ListEntitiesRequest.builder()
				.catalog(AWS_MP_CATALOG)
				.entityType(ENTITY_TYPE_OFFER)
				.maxResults(10)
				.nextToken(null)
				.build();

		ListEntitiesResponse listEntitiesResponse = marketplaceCatalogClient.listEntities(listEntitiesRequest);

		for (EntitySummary entitySummary : listEntitiesResponse.entitySummaryList()) {
			entityIdList.add(entitySummary.entityId());
		}

		while (listEntitiesResponse.nextToken() != null) {
			listEntitiesRequest = 
					ListEntitiesRequest.builder()
					.catalog(AWS_MP_CATALOG)
					.entityType(ENTITY_TYPE_OFFER)
					.maxResults(10)
					.nextToken(listEntitiesResponse.nextToken())
					.build();
			listEntitiesResponse = marketplaceCatalogClient.listEntities(listEntitiesRequest);

			for (EntitySummary entitySummary : listEntitiesResponse.entitySummaryList()) {
				entityIdList.add(entitySummary.entityId());
			}
		}

		// filter for CPPO offers: ResaleAuthorizationId exists in Details

		List<String> cppoOfferIds = new ArrayList<String>();
		
		for (String entityId : entityIdList) {
			DescribeEntityRequest describeEntityRequest = 
					DescribeEntityRequest.builder()
					.catalog(AWS_MP_CATALOG)
					.entityId(entityId)
					.build();
			DescribeEntityResponse describeEntityResponse = marketplaceCatalogClient.describeEntity(describeEntityRequest);
			
			Document resaleAuthorizationDocument = describeEntityResponse.detailsDocument().asMap().get(ATTRIBUTE_RESALE_AUTHORIZATION_ID);
			String resaleAuthorizationId = resaleAuthorizationDocument != null ? resaleAuthorizationDocument.asString() : "";

			if (!resaleAuthorizationId.isEmpty()) {
			    cppoOfferIds.add(resaleAuthorizationId);
			}
		}

		ReferenceCodesUtils.formatOutput(cppoOfferIds);
	}

}
