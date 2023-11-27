package com.amazon.samplelib.capi;

import java.util.ArrayList;
import java.util.List;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

import software.amazon.awssdk.services.marketplacecatalog.MarketplaceCatalogClient;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityResponse;
import software.amazon.awssdk.services.marketplacecatalog.model.EntitySummary;
import software.amazon.awssdk.services.marketplacecatalog.model.ListEntitiesRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.ListEntitiesResponse;

public class ListPrivateOffers {

	public static final MarketplaceCatalogClient awsMarketplaceCatalog = ReferenceCodesUtils.getMPCatalogClient();

	public static void main(String[] args) {

		List<EntitySummary> offerEntityList = getEntitySummaryList("Offer", "Private");

		List<EntityDetailOffer> offerWithDetails = new ArrayList<EntityDetailOffer>();

		for (EntitySummary oes : offerEntityList) {
			EntityDetailOffer edo = new EntityDetailOffer(oes, getEntityDetails(oes));
			offerWithDetails.add(edo);
		}
		ReferenceCodesUtils.printResult(offerWithDetails);
	}

	private static String getEntityDetails(EntitySummary es) {
		DescribeEntityRequest dreq = DescribeEntityRequest.builder().catalog(ReferenceCodesConstants.AWS_MP_CATALOG).entityId(es.entityId()).build();
		DescribeEntityResponse dresult = awsMarketplaceCatalog.describeEntity(dreq);
		String details = dresult.details();
		return details;
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

	static class EntityDetailOffer {
		EntitySummary entitySummary;
		String offerDetail;

		EntityDetailOffer(EntitySummary entitySummary, String offerDetail) {
			this.entitySummary = entitySummary;
			this.offerDetail = offerDetail;
		}
	}

}
