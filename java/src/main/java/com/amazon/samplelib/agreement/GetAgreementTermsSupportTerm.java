//AG-18 Obtain the EULA I have entered into with my customer via the agreement
package com.amazon.samplelib.agreement;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.DocumentItem;
import software.amazon.awssdk.services.marketplaceagreement.model.SupportTerm;

import java.util.ArrayList;
import java.util.List;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

public class GetAgreementTermsSupportTerm {
	
	static String agreementId = ReferenceCodesConstants.AGREEMENT_ID;

	public static void main(String[] args) {
		
		MarketplaceAgreementClient mpasClient = ReferenceCodesUtils.getMPAgreementClient();
		
		List<AcceptedTerm> acceptedTerms = ReferenceCodesUtils.getAgreementAcceptedTerms(mpasClient, agreementId);
		
		List<SupportTerm> supportTerms = new ArrayList<>();
        
		for (AcceptedTerm aterm : acceptedTerms) {
			if ( aterm.supportTerm() != null ) {
				supportTerms.add(aterm.supportTerm());
			}
		}
		
		ReferenceCodesUtils.printResult(supportTerms);
	}

}
