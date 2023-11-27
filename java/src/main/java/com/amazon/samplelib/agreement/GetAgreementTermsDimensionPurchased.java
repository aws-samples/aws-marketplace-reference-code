//AG-28 Obtain the auto-renewal status of the agreement
package com.amazon.samplelib.agreement;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.Dimension;

import java.util.ArrayList;
import java.util.List;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

public class GetAgreementTermsDimensionPurchased {
	
	static String agreementId = ReferenceCodesConstants.AGREEMENT_ID;

	public static void main(String[] args) {
		
		MarketplaceAgreementClient mpasClient = ReferenceCodesUtils.getMPAgreementClient();
		
		List<AcceptedTerm> acceptedTerms = ReferenceCodesUtils.getAgreementAcceptedTerms(mpasClient, agreementId);
		
		List<String> dimensionKeys = new ArrayList<String>();
		for (AcceptedTerm aterm : acceptedTerms) {
			if ( aterm.configurableUpfrontPricingTerm() != null ) {
				if (aterm.configurableUpfrontPricingTerm().configuration().selectorValue() != null ) {
					List<Dimension> dimensions = aterm.configurableUpfrontPricingTerm().configuration().dimensions();
					for (Dimension d : dimensions) {
						dimensionKeys.add(d.dimensionKey());
					}
				}
				
			}
		}
		
		ReferenceCodesUtils.printResult(dimensionKeys);
	}
}
