package com.example.awsmarketplace.catalogapi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

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
import software.amazon.awssdk.services.marketplacecatalog.model.BatchDescribeEntitiesRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.EntityRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.BatchDescribeEntitiesResponse;
import software.amazon.awssdk.services.marketplacecatalog.model.EntityDetail;

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
		List<EntityRequest> describeEntityRequestList = new ArrayList<EntityRequest>();
		for (String entityId : entityIdList) {
			EntityRequest describeEntityRequest = EntityRequest.builder()
					.catalog(AWS_MP_CATALOG)
					.entityId(entityId)
					.build();
			describeEntityRequestList.add(describeEntityRequest);
			if(describeEntityRequestList.size() == 20) {
				BatchDescribeEntitiesRequest batchDescribeEntitiesRequest = BatchDescribeEntitiesRequest.builder()
						.entityRequestList(describeEntityRequestList).build();
				BatchDescribeEntitiesResponse batchDescribeEntitiesResponse = marketplaceCatalogClient.batchDescribeEntities(batchDescribeEntitiesRequest);
				cppoOfferIds.addAll(getResaleAuthorizationIdsFromOfferDocuments(batchDescribeEntitiesResponse.entityDetails()));
				describeEntityRequestList.clear();
			}
		}
		if(!describeEntityRequestList.isEmpty()) {
			BatchDescribeEntitiesRequest batchDescribeEntitiesRequest = BatchDescribeEntitiesRequest.builder()
					.entityRequestList(describeEntityRequestList).build();
			BatchDescribeEntitiesResponse batchDescribeEntitiesResponse = marketplaceCatalogClient.batchDescribeEntities(batchDescribeEntitiesRequest);
			cppoOfferIds.addAll(getResaleAuthorizationIdsFromOfferDocuments(batchDescribeEntitiesResponse.entityDetails()));
		}

		ReferenceCodesUtils.formatOutput(cppoOfferIds);
	}

	private static List<String> getResaleAuthorizationIdsFromOfferDocuments(Map<String, EntityDetail> entityDetailsMap) {
		List<String> cppoOfferIds = new ArrayList<String>();
		for (Map.Entry<String, EntityDetail> entry : entityDetailsMap.entrySet()) {
			Document resaleAuthorizationDocument = entry.getValue().detailsDocument().asMap().get(ATTRIBUTE_RESALE_AUTHORIZATION_ID);
			String resaleAuthorizationId = resaleAuthorizationDocument != null ? resaleAuthorizationDocument.asString() : "";
			if (!resaleAuthorizationId.isEmpty()) {
				cppoOfferIds.add(resaleAuthorizationId);
			}
		}
		return cppoOfferIds;
	}

}
