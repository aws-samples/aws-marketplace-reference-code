package com.example.awsmarketplace.catalogapi;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.*;
import com.example.awsmarketplace.utils.ReferenceCodesUtils;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplacecatalog.MarketplaceCatalogClient;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityResponse;
import software.amazon.awssdk.services.marketplacecatalog.model.EntitySummary;
import software.amazon.awssdk.services.marketplacecatalog.model.EntityTypeFilters;
import software.amazon.awssdk.services.marketplacecatalog.model.ListEntitiesRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.ListEntitiesResponse;
import software.amazon.awssdk.services.marketplacecatalog.model.OfferAvailabilityEndDateFilter;
import software.amazon.awssdk.services.marketplacecatalog.model.OfferAvailabilityEndDateFilterDateRange;
import software.amazon.awssdk.services.marketplacecatalog.model.OfferBuyerAccountsFilter;
import software.amazon.awssdk.services.marketplacecatalog.model.OfferFilters;
import software.amazon.awssdk.services.marketplacecatalog.model.OfferReleaseDateFilter;
import software.amazon.awssdk.services.marketplacecatalog.model.OfferReleaseDateFilterDateRange;
import software.amazon.awssdk.services.marketplacecatalog.model.OfferTargetingFilter;
import software.amazon.awssdk.services.marketplacecatalog.model.BatchDescribeEntitiesRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.EntityRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.BatchDescribeEntitiesResponse;
import software.amazon.awssdk.services.marketplacecatalog.model.EntityDetail;

public class ListAllPrivateOffers {

	/*
	 * List all my private offers and sort or filter them by Offer Publish Date, Offer Expiry Date and Buyer IDs
	 * 
	 * OfferTargetingFilter = BuyerAccounts (private offer);
	 * OfferBuyerAccountsFilter: Buyer IDs filter
	 * OfferAvailabilityEndDateFilter : Offer Expiry Date filter
	 * OfferReleaseDateFilter : Offer Publish Date filter
	 */
	public static void main(String[] args) {

		MarketplaceCatalogClient marketplaceCatalogClient = 
				MarketplaceCatalogClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();

		String offerReleaseDateAfterValue = "2023-01-01T23:59:59Z";
		String offerAvailableEndDateAfterValue = "2040-12-24T23:59:59Z";
		
		EntityTypeFilters entityTypeFilters = 
				EntityTypeFilters.builder()
				.offerFilters(OfferFilters.builder()
						.targeting(OfferTargetingFilter.builder()
								.valueListWithStrings(OFFER_TARGETING_BUYERACCOUNTS)
								.build())
						.buyerAccounts(OfferBuyerAccountsFilter.builder()
								.wildCardValue(BUYER_ACCOUNT_ID)
								.build())
						.availabilityEndDate(OfferAvailabilityEndDateFilter.builder()
								.dateRange(OfferAvailabilityEndDateFilterDateRange.builder()
										.afterValue(offerAvailableEndDateAfterValue).build())
								.build())
						.releaseDate(OfferReleaseDateFilter.builder()
								.dateRange(OfferReleaseDateFilterDateRange.builder()
										.afterValue(offerReleaseDateAfterValue)
										.build())
								.build())
						.build())
				.build();
			
		ListEntitiesRequest listEntitiesRequest = 
				ListEntitiesRequest.builder()
				.catalog(AWS_MP_CATALOG)
				.entityType(ENTITY_TYPE_OFFER).maxResults(10)
				.entityTypeFilters(entityTypeFilters)
				.nextToken(null)
				.build();
		
		ListEntitiesResponse listEntitiesResponse = marketplaceCatalogClient.listEntities(listEntitiesRequest);
		List<EntitySummary> entitySummaryList = new ArrayList<EntitySummary>();
		
		entitySummaryList.addAll(listEntitiesResponse.entitySummaryList());
		
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
			entitySummaryList.addAll(listEntitiesResponse.entitySummaryList());
		}

		// for each offer id, output the offer detail using BatchDescribeEntities API

		List<EntityRequest> describeEntityRequestList = new ArrayList<EntityRequest>();
		List<EntityDetail> describeEntityResponseList = new ArrayList<EntityDetail>();
		for (EntitySummary entitySummary : entitySummaryList) {
			EntityRequest describeEntityRequest = EntityRequest.builder()
					.catalog(AWS_MP_CATALOG)
					.entityId(entitySummary.entityId())
					.build();
			describeEntityRequestList.add(describeEntityRequest);
			if(describeEntityRequestList.size() == 20) {
				BatchDescribeEntitiesRequest batchDescribeEntitiesRequest = BatchDescribeEntitiesRequest.builder()
						.entityRequestList(describeEntityRequestList).build();
				BatchDescribeEntitiesResponse batchDescribeEntitiesResponse = marketplaceCatalogClient.batchDescribeEntities(batchDescribeEntitiesRequest);
				describeEntityResponseList.addAll(batchDescribeEntitiesResponse.entityDetails().values());
				describeEntityRequestList.clear();
			}
		}
		if(!describeEntityRequestList.isEmpty()) {
			BatchDescribeEntitiesRequest batchDescribeEntitiesRequest = BatchDescribeEntitiesRequest.builder()
					.entityRequestList(describeEntityRequestList).build();
			BatchDescribeEntitiesResponse batchDescribeEntitiesResponse = marketplaceCatalogClient.batchDescribeEntities(batchDescribeEntitiesRequest);
			describeEntityResponseList.addAll(batchDescribeEntitiesResponse.entityDetails().values());
		}
		describeEntityResponseList.forEach(response -> System.out.println(response));
	}

}
