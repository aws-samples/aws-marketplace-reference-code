package com.amazon.samplelib.capi;

import java.util.ArrayList;
import java.util.List;

import com.amazon.samplelib.Entity.Details;
import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.ToNumberPolicy;

import software.amazon.awssdk.services.marketplacecatalog.MarketplaceCatalogClient;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityResponse;
import software.amazon.awssdk.services.marketplacecatalog.model.EntitySummary;
import software.amazon.awssdk.services.marketplacecatalog.model.ListEntitiesRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.ListEntitiesResponse;

public class ListAllCppoOffers {

	private static Gson gson = new GsonBuilder().setObjectToNumberStrategy(ToNumberPolicy.LAZILY_PARSED_NUMBER).create();

	public static final MarketplaceCatalogClient awsMarketplaceCatalog = ReferenceCodesUtils.getMPCatalogClient();

	public static void main(String[] args) {

		List<EntitySummary> offerEntityList = getEntitySummaryList("Offer", null);

		List<String> offerIds = getCppoOfferIds(offerEntityList);

		ReferenceCodesUtils.printResult(offerIds);
	}

	private static String getEntityDetails(EntitySummary es) {
		DescribeEntityRequest dreq = DescribeEntityRequest.builder().catalog(ReferenceCodesConstants.AWS_MP_CATALOG).entityId(es.entityId()).build();
		DescribeEntityResponse dresult = awsMarketplaceCatalog.describeEntity(dreq);
		String details = dresult.details();
		
		return details;
	}


	private static List<String> getCppoOfferIds ( List<EntitySummary> entitySummaryList) {
		List<String> cppoOfferIds = new ArrayList<String>();
		for (EntitySummary es : entitySummaryList) {
			String details = getEntityDetails(es);
			Details detail = gson.fromJson(details, Details.class);
			String resaleId = detail.ResaleAuthorizationId;
			if (resaleId != null && resaleId.length() > 0) {
				System.out.println("adding " + resaleId);
				cppoOfferIds.add(es.entityId());
			}
		}
		return cppoOfferIds;
	}
	
	private static List<EntitySummary> getEntitySummaryList(String entityType, String visibility) {
		List<EntitySummary> entityList = new ArrayList<EntitySummary>();
		
		ListEntitiesRequest request = ListEntitiesRequest.builder().catalog(ReferenceCodesConstants.AWS_MP_CATALOG).entityType(entityType).maxResults(50).nextToken(null).build();

		ListEntitiesResponse result = awsMarketplaceCatalog.listEntities(request);

		for (EntitySummary es : result.entitySummaryList()) {
			if (visibility == null || visibility.equals(es.visibility())) {
				entityList.add(es);
			}
		}

		while (result.nextToken() != null) {
			request = ListEntitiesRequest.builder().catalog(visibility).catalog(ReferenceCodesConstants.AWS_MP_CATALOG).entityType(entityType)
					.maxResults(10).nextToken(result.nextToken()).build();
			result = awsMarketplaceCatalog.listEntities(request);

			for (EntitySummary es : result.entitySummaryList()) {
				if (visibility == null || visibility.equals(es.visibility())) {
					entityList.add(es);
				}
			}
		}

		return entityList;

	}
}
