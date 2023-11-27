package com.amazon.samplelib.capi;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

import software.amazon.awssdk.services.marketplacecatalog.MarketplaceCatalogClient;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityResponse;

public class DescribeEntity {

	public static void main(String[] args) {

		String prodId = ReferenceCodesConstants.OFFER_ID;

		MarketplaceCatalogClient awsMarketplaceCatalog = ReferenceCodesUtils.getMPCatalogClient();

		DescribeEntityRequest request = DescribeEntityRequest.builder().catalog(ReferenceCodesConstants.AWS_MP_CATALOG).entityId(prodId)
				.build();

		DescribeEntityResponse result = awsMarketplaceCatalog.describeEntity(request);

		ReferenceCodesUtils.printResult(result);
	}
}
