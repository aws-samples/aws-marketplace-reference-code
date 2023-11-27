//AG-30 instances of each dimension that buyer has purchased in the agreement
package com.amazon.samplelib.agreement;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.Dimension;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

public class GetAgreementTermsDimensionInstances {
	
	static String agreementId = ReferenceCodesConstants.AGREEMENT_ID;

	public static void main(String[] args) {
		
		MarketplaceAgreementClient mpasClient = ReferenceCodesUtils.getMPAgreementClient();
		
		List<AcceptedTerm> acceptedTerms = ReferenceCodesUtils.getAgreementAcceptedTerms(mpasClient, agreementId);
		
		Map <String, List<Dimension>> dimensionMap = new HashMap<String, List<Dimension>>();
		
		for (AcceptedTerm aterm : acceptedTerms) {
			List<Dimension> dimensionsList = new ArrayList<Dimension>();
			if ( aterm.configurableUpfrontPricingTerm() != null ) {
				String selectorValue = ""; 
				if ( aterm.configurableUpfrontPricingTerm().configuration() != null ) {
					if ( aterm.configurableUpfrontPricingTerm().configuration().selectorValue() != null) {
						selectorValue = aterm.configurableUpfrontPricingTerm().configuration().selectorValue();
					}
					if ( aterm.configurableUpfrontPricingTerm().configuration().hasDimensions()) {
						dimensionsList = aterm.configurableUpfrontPricingTerm().configuration().dimensions();
					}
				}
				if ( selectorValue.length() > 0 ) {
					dimensionMap.put(selectorValue,  dimensionsList);
				}
			}
		}
		
		ReferenceCodesUtils.printResult(dimensionMap);
	}
}
