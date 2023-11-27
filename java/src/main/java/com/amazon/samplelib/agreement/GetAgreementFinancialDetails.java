//AG-14 Obtain financial details, such as Total Contract Value of the agreementfrom a given agreement
package com.amazon.samplelib.agreement;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementResponse;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

public class GetAgreementFinancialDetails {

	static String agreementId = ReferenceCodesConstants.AGREEMENT_ID;

	public static void main(String[] args) {
		
		MarketplaceAgreementClient mpasClient = ReferenceCodesUtils.getMPAgreementClient();

		DescribeAgreementResponse result = ReferenceCodesUtils.getDescribeAgreementResult(mpasClient, agreementId);
		
		String tcv = result.estimatedCharges().agreementValue()+ " " + result.estimatedCharges().currencyCode();
		
		ReferenceCodesUtils.printResult(tcv);

	}
}
