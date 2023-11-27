//AG-29 Obtain pricing per each dimension in the agreement
package com.amazon.samplelib.agreement;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.FreeTrialPricingTerm;

import java.util.ArrayList;
import java.util.List;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

public class GetAgreementTermsFreeTrialDetails {
	
	static String agreementId = ReferenceCodesConstants.AGREEMENT_ID;

	public static void main(String[] args) {
		
		MarketplaceAgreementClient mpasClient = ReferenceCodesUtils.getMPAgreementClient();

		List<AcceptedTerm> acceptedTerms = ReferenceCodesUtils.getAgreementAcceptedTerms(mpasClient, agreementId);
		
		List<FreeTrialPricingTerm> freeTrialPricingTerms = new ArrayList<FreeTrialPricingTerm>();
		
		for (AcceptedTerm aterm : acceptedTerms) {
			if ( aterm.freeTrialPricingTerm() != null ) {
				freeTrialPricingTerms.add(aterm.freeTrialPricingTerm());	
			}
		}
		
		ReferenceCodesUtils.printResult(freeTrialPricingTerms);
	}
}
