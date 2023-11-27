package com.amazon.samplelib.agreement;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsResponse;

import com.amazon.samplelib.utils.ReferenceCodesUtils;

public class GetAgreementTerms {
	
	static String agreementId = ReferenceCodesConstants.AGREEMENT_ID;

	public static void main(String[] args) {
		
		MarketplaceAgreementClient mpasClient = ReferenceCodesUtils.getMPAgreementClient();

		GetAgreementTermsResponse result = ReferenceCodesUtils.getAgreementTerms(mpasClient, agreementId);
		
		ReferenceCodesUtils.printResult(result);
		
	}

}
