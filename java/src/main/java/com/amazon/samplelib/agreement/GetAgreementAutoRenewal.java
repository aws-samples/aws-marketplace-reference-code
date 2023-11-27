//AG-28 Obtain the dimensions the buyer has purchased from me via the agreement
package com.amazon.samplelib.agreement;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptedTerm;

import java.util.List;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

public class GetAgreementAutoRenewal {
	
	static String agreementId = ReferenceCodesConstants.AGREEMENT_ID;
	
	public static void main(String[] args) {
		
		MarketplaceAgreementClient mpasClient = ReferenceCodesUtils.getMPAgreementClient();
		
		List<AcceptedTerm> acceptedTerms = ReferenceCodesUtils.getAgreementAcceptedTerms(mpasClient, agreementId);
		
		String autoRenewal = "No Auto Renewal";
		
		for (AcceptedTerm aterm : acceptedTerms) {
			if ( aterm.renewalTerm() != null && aterm.renewalTerm().configuration() != null ) {
				autoRenewal = aterm.renewalTerm().configuration().enableAutoRenew().toString();
				break;
			}
		}
		
		ReferenceCodesUtils.printResult(autoRenewal);
	}

}
