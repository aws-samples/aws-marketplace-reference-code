package com.amazon.samplelib.capi;

import java.util.ArrayList;
import java.util.List;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

import software.amazon.awssdk.services.marketplacecatalog.MarketplaceCatalogClient;
import software.amazon.awssdk.services.marketplacecatalog.model.ListEntitiesRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.ListEntitiesResponse;

public class ListAllSharedResaleAuthorizations {

	public static final MarketplaceCatalogClient awsMarketplaceCatalog = ReferenceCodesUtils.getMPCatalogClient();

	public static void main(String[] args) {

		List<ListEntitiesResponse> responseList = getEntitySummaryList("ResaleAuthorization");

		ReferenceCodesUtils.printResult(responseList);
	}

	private static List<ListEntitiesResponse> getEntitySummaryList(String entityType) {
		List<ListEntitiesResponse> responseList = new ArrayList<ListEntitiesResponse>();
		
		ListEntitiesRequest request = ListEntitiesRequest
										.builder()
										.catalog(ReferenceCodesConstants.AWS_MP_CATALOG)
										.entityType(entityType)
										.maxResults(50)
										.ownershipType(ReferenceCodesConstants.OwnershipTypeShared)
										.nextToken(null)
										.build();

		ListEntitiesResponse result = awsMarketplaceCatalog.listEntities(request);

		responseList.add(result);

		while (result.nextToken() != null) {
			request = ListEntitiesRequest
					.builder()
					.catalog(ReferenceCodesConstants.AWS_MP_CATALOG)
					.entityType(entityType)
					.maxResults(50)
					.ownershipType(ReferenceCodesConstants.OwnershipTypeShared)
					.nextToken(result.nextToken())
					.build();

			result = awsMarketplaceCatalog.listEntities(request);
			
			responseList.add(result);
		}

		return responseList;

	}
}
