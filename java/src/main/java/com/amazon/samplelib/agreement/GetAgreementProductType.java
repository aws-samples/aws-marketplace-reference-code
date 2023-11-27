//AG-11 Obtain the Product Type of the product the agreement was created on
package com.amazon.samplelib.agreement;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.Resource;

import java.util.ArrayList;
import java.util.List;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

public class GetAgreementProductType {
	
	static String agreementId = ReferenceCodesConstants.AGREEMENT_ID;

	public static void main(String[] args) {
		
		MarketplaceAgreementClient mpasClient = ReferenceCodesUtils.getMPAgreementClient();

		DescribeAgreementResponse result = ReferenceCodesUtils.getDescribeAgreementResult(mpasClient, agreementId);
		
		List<String> productIds = new ArrayList<String>();
		for (Resource summary : result.proposalSummary().resources()) {
			productIds.add(summary.id() + ":" + summary.type());
		}
			
		ReferenceCodesUtils.printResult(productIds);
	}
}
