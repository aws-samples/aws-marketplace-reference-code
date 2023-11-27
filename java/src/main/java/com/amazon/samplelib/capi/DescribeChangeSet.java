package com.amazon.samplelib.capi;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

import software.amazon.awssdk.services.marketplacecatalog.MarketplaceCatalogClient;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeChangeSetRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeChangeSetResponse;


public class DescribeChangeSet {

	public static void main(String[] args) {
		
		String changeSetId = ReferenceCodesConstants.CHANGESET_ID;

		MarketplaceCatalogClient awsMarketplaceCatalog = ReferenceCodesUtils.getMPCatalogClient();
		
		DescribeChangeSetRequest request = 
				DescribeChangeSetRequest.builder()
				.catalog(ReferenceCodesConstants.AWS_MP_CATALOG)
				.changeSetId(changeSetId)
				.build();
 
		DescribeChangeSetResponse result = awsMarketplaceCatalog.describeChangeSet(request);

		ReferenceCodesUtils.printResult(result);	
	}
}

