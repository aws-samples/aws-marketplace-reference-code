//AG-29 Obtain pricing per each dimension in the agreement
package com.amazon.samplelib.agreement;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptedTerm;

import java.util.ArrayList;
import java.util.List;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

public class GetAgreementTermsPricingEachDimension {
	
	static String agreementId = ReferenceCodesConstants.AGREEMENT_ID;

	public static void main(String[] args) {
		
		MarketplaceAgreementClient mpasClient = ReferenceCodesUtils.getMPAgreementClient();

		List<AcceptedTerm> acceptedTerms = ReferenceCodesUtils.getAgreementAcceptedTerms(mpasClient, agreementId);
		
		List<Object> dimensions = new ArrayList<Object>();
		
		for (AcceptedTerm aterm : acceptedTerms) {
			List<Object> rateInfo = new ArrayList<Object>();
			if ( aterm.configurableUpfrontPricingTerm() != null ) {
				if ( aterm.configurableUpfrontPricingTerm().type() != null  ) {
					rateInfo.add(aterm.configurableUpfrontPricingTerm().type());
				}
				if ( aterm.configurableUpfrontPricingTerm().currencyCode() != null ) {
					rateInfo.add(aterm.configurableUpfrontPricingTerm().currencyCode());
				}
				if ( aterm.configurableUpfrontPricingTerm().hasRateCards() ) {
					rateInfo.add(aterm.configurableUpfrontPricingTerm().rateCards());
				}
				dimensions.add(rateInfo);	
			}
		}
		
		ReferenceCodesUtils.printResult(dimensions);
	}
}
