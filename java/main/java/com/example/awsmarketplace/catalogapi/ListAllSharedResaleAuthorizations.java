package com.example.awsmarketplace.catalogapi;

import java.util.ArrayList;
import java.util.List;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.*;
import com.example.awsmarketplace.utils.ReferenceCodesUtils;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplacecatalog.MarketplaceCatalogClient;
import software.amazon.awssdk.services.marketplacecatalog.model.ListEntitiesRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.ListEntitiesResponse;

public class ListAllSharedResaleAuthorizations {

	/*
	 * list all resale authorizations shared to an account
	 */
	public static void main(String[] args) {
		
		MarketplaceCatalogClient marketplaceCatalogClient = 
				MarketplaceCatalogClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();
		
		List<ListEntitiesResponse> responseList = new ArrayList<ListEntitiesResponse>();

		ListEntitiesRequest listEntitiesRequest = 
				ListEntitiesRequest.builder()
				.catalog(AWS_MP_CATALOG)
				.entityType(ENTITY_TYPE_RESALE_AUTHORIZATION)
				.maxResults(10)
				.ownershipType(OWNERSHIP_TYPE_SHARED)
				.nextToken(null)
				.build();

		ListEntitiesResponse listEntitiesResponse = marketplaceCatalogClient.listEntities(listEntitiesRequest);

		responseList.add(listEntitiesResponse);

		while (listEntitiesResponse.nextToken() != null) {
			listEntitiesRequest = ListEntitiesRequest.builder()
					.catalog(AWS_MP_CATALOG)
					.entityType(ENTITY_TYPE_RESALE_AUTHORIZATION)
					.maxResults(10)
					.ownershipType(OWNERSHIP_TYPE_SHARED)
					.nextToken(listEntitiesResponse.nextToken())
					.build();

			listEntitiesResponse = marketplaceCatalogClient.listEntities(listEntitiesRequest);

			responseList.add(listEntitiesResponse);
		}
		ReferenceCodesUtils.formatOutput(responseList);
	}
	
}
