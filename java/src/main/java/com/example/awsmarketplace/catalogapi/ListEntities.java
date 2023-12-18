package com.example.awsmarketplace.catalogapi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.*;
import com.example.awsmarketplace.utils.ReferenceCodesUtils;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplacecatalog.MarketplaceCatalogClient;
import software.amazon.awssdk.services.marketplacecatalog.model.EntitySummary;
import software.amazon.awssdk.services.marketplacecatalog.model.EntityTypeFilters;
import software.amazon.awssdk.services.marketplacecatalog.model.ListEntitiesRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.ListEntitiesResponse;
import software.amazon.awssdk.services.marketplacecatalog.model.OfferFilters;
import software.amazon.awssdk.services.marketplacecatalog.model.OfferProductIdFilter;
import software.amazon.awssdk.services.marketplacecatalog.model.OfferStateFilter;
import software.amazon.awssdk.services.marketplacecatalog.model.OfferTargetingFilter;

public class ListEntities {

	private static MarketplaceCatalogClient marketplaceCatalogClient = 
			MarketplaceCatalogClient.builder()
			.httpClient(ApacheHttpClient.builder().build())
			.credentialsProvider(ProfileCredentialsProvider.create())
			.build();

	/*
	 * List all my AMI or SaaS or Container products and associated public offers
	 */
	public static void main(String[] args) {
		Map<String, List<EntitySummary>> allProductsWithOffers = new HashMap<String, List<EntitySummary>> ();

		// get all product entities
		List<EntitySummary> productEntityList = new ArrayList<EntitySummary>();

		ListEntitiesRequest listEntitiesRequest = 
				ListEntitiesRequest.builder()
				.catalog(AWS_MP_CATALOG)
				.entityType(PRODUCT_TYPE_AMI)
				.maxResults(10)
				.nextToken(null)
				.build();
		
	 
		ListEntitiesResponse listEntitiesResponse = marketplaceCatalogClient.listEntities(listEntitiesRequest);

		productEntityList.addAll(listEntitiesResponse.entitySummaryList());


		while (listEntitiesResponse.nextToken() != null) {
			listEntitiesRequest = 
					ListEntitiesRequest.builder()
					.catalog(AWS_MP_CATALOG)
					.entityType(PRODUCT_TYPE_AMI)
					.maxResults(10)
					.nextToken(listEntitiesResponse.nextToken())
					.build();
			listEntitiesResponse = marketplaceCatalogClient.listEntities(listEntitiesRequest);
			productEntityList.addAll(listEntitiesResponse.entitySummaryList());
		}
		
		// loop through each product entity and get the public released offers associated using product id filter
		
		for ( EntitySummary productEntitySummary : productEntityList) {
			EntityTypeFilters entityTypeFilters = 
					EntityTypeFilters.builder()
					.offerFilters(OfferFilters.builder()
							.targeting(OfferTargetingFilter.builder()
									.valueListWithStrings(OFFER_TARGETING_NONE)
									.build())
							.state(OfferStateFilter.builder()
									.valueListWithStrings(OFFER_STATE_RELEASED)
									.build())
							.productId(OfferProductIdFilter.builder()
									.valueList(productEntitySummary.entityId())
									.build())
							.build())
					.build();
			
			listEntitiesRequest = 
					ListEntitiesRequest.builder()
					.catalog(AWS_MP_CATALOG)
					.entityType(ENTITY_TYPE_OFFER)
					.maxResults(10)
					.entityTypeFilters(entityTypeFilters)
					.nextToken(null)
					.build();
			
			listEntitiesResponse = marketplaceCatalogClient.listEntities(listEntitiesRequest);
			
			// save all entitySummary of the results into entitySummaryList
			
			List<EntitySummary> offerEntitySummaryList = new ArrayList<EntitySummary>();
			
			offerEntitySummaryList.addAll(listEntitiesResponse.entitySummaryList());
			
			while ( listEntitiesResponse.nextToken() != null && listEntitiesResponse.nextToken().length() > 0) {
				listEntitiesRequest = 
						ListEntitiesRequest.builder()
						.catalog(AWS_MP_CATALOG)
						.entityType(ENTITY_TYPE_OFFER)
						.maxResults(10)
						.entityTypeFilters(entityTypeFilters)
						.nextToken(listEntitiesResponse.nextToken())
						.build();
				listEntitiesResponse = marketplaceCatalogClient.listEntities(listEntitiesRequest);
				offerEntitySummaryList.addAll(listEntitiesResponse.entitySummaryList());
			}
			
			// save final results into map; key = product id; value = offer entity summary list
			
			allProductsWithOffers.put(productEntitySummary.entityId(), offerEntitySummaryList);
		}
	
		ReferenceCodesUtils.formatOutput(allProductsWithOffers);
	}

}
