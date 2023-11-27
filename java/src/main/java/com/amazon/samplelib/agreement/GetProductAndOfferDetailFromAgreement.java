package com.amazon.samplelib.agreement;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.Resource;
import java.util.ArrayList;
import java.util.List;

import software.amazon.awssdk.services.marketplacecatalog.MarketplaceCatalogClient;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityResponse;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

public class GetProductAndOfferDetailFromAgreement {
	
	static String agreementId = ReferenceCodesConstants.AGREEMENT_ID;

	public static void main(String[] args) {
		
		MarketplaceAgreementClient mpasClient = ReferenceCodesUtils.getMPAgreementClient();

		DescribeAgreementResponse result = ReferenceCodesUtils.getDescribeAgreementResult(mpasClient, agreementId);
		
		String offerId = result.proposalSummary().offerId();
		
		List<String> productIds = new ArrayList<String>();
		for (Resource summary : result.proposalSummary().resources()) {
			productIds.add(summary.id());
		}

		MarketplaceCatalogClient awsMarketplaceCatalog = ReferenceCodesUtils.getMPCatalogClient();
			
		DescribeEntityRequest request = 
				DescribeEntityRequest.builder()
				.catalog(ReferenceCodesConstants.AWS_MP_CATALOG)
				.entityId(offerId).build();
		
		DescribeEntityResponse resultcapi = awsMarketplaceCatalog.describeEntity(request);
		
		System.out.println("Print details for offer " + offerId);
		
		ReferenceCodesUtils.printResult(resultcapi);
		
		for ( String productId : productIds) {
			request = DescribeEntityRequest.builder()
					.catalog(ReferenceCodesConstants.AWS_MP_CATALOG)
					.entityId(productId).build();
			resultcapi = awsMarketplaceCatalog.describeEntity(request);
			System.out.println("Print details for product " + productId);
			ReferenceCodesUtils.printResult(resultcapi);
		}
		
	}
}
