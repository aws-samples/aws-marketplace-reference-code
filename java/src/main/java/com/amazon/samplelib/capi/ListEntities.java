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

public class ListEntities {

	static String productType = ReferenceCodesConstants.PRODUCT_TYPE_AMI;

	public static MarketplaceCatalogClient awsMarketplaceCatalog = ReferenceCodesUtils.getMPCatalogClient();

	public static void main(String[] args) {

		List<EntitySummary> productEntityList = getEntitySummaryList(productType, null);

		List<EntitySummary> offerEntityList = getEntitySummaryList("Offer", "Public");

		List<EntityDetailOffer> productWithDetails = new ArrayList<EntityDetailOffer>();

		for (EntitySummary es : productEntityList) {
			EntityDetailOffer edo = new EntityDetailOffer(es, getEntityDetails(es), null);
			for (EntitySummary oes : offerEntityList) {
				String details = getEntityDetails(oes);
				if (details.contains(es.entityId())) {
					edo = new EntityDetailOffer(es, getEntityDetails(es), details);
					break;
				}
			}
			productWithDetails.add(edo);
		}
		ReferenceCodesUtils.printResult(productWithDetails);
	}

	private static String getEntityDetails(EntitySummary es) {
		DescribeEntityRequest dreq = DescribeEntityRequest.builder().catalog("AWSMarketplace").entityId(es.entityId()).build();
		DescribeEntityResponse dresult = awsMarketplaceCatalog.describeEntity(dreq);
		String details = dresult.details();
		return details;
	}

	private static List<EntitySummary> getEntitySummaryList(String entityType, String visibility) {
		List<EntitySummary> entityList = new ArrayList<EntitySummary>();

		ListEntitiesRequest request = ListEntitiesRequest.builder().catalog("AWSMarketplace").entityType(entityType).maxResults(50).nextToken(null).build();

		ListEntitiesResponse result = awsMarketplaceCatalog.listEntities(request);

		for (EntitySummary es : result.entitySummaryList()) {
			if (visibility == null || visibility.equals(es.visibility())) {
				entityList.add(es);
			}
		}

		while (result.nextToken() != null) {
			request = ListEntitiesRequest.builder().catalog(visibility).catalog("AWSMarketplace").entityType(entityType)
					.maxResults(10).nextToken(result.nextToken()).build();
			result = awsMarketplaceCatalog.listEntities(request);

			for (EntitySummary es : result.entitySummaryList()) {
				System.out.println("Entity id = " + es.entityId());

				if (visibility == null || visibility.equals(es.visibility())) {
					entityList.add(es);
				}
			}
		}

		return entityList;

	}

	static class EntityDetailOffer {
		EntitySummary entitySummary;
		String productDetail;
		String offerDetail;

		EntityDetailOffer(EntitySummary entitySummary, String productDetail, String offerDetail) {
			this.entitySummary = entitySummary;
			this.productDetail = productDetail;
			this.offerDetail = offerDetail;
		}
	}

}
