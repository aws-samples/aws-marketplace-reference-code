//AG-18 Obtain the EULA I have entered into with my customer via the agreement
package com.amazon.samplelib.agreement;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.DocumentItem;

import java.util.ArrayList;
import java.util.List;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

public class GetAgreementTermsEula {
	
	static String agreementId = ReferenceCodesConstants.AGREEMENT_ID;

	public static void main(String[] args) {
		
		MarketplaceAgreementClient mpasClient = ReferenceCodesUtils.getMPAgreementClient();
		
		List<AcceptedTerm> acceptedTerms = ReferenceCodesUtils.getAgreementAcceptedTerms(mpasClient, agreementId);
		
		List<DocumentItem> leganEulaArray = new ArrayList<>();
        
		for (AcceptedTerm aterm : acceptedTerms) {
			if ( aterm.legalTerm() != null ) {
				if ( aterm.legalTerm().hasDocuments()) {
					for ( DocumentItem docItem : aterm.legalTerm().documents()) {
						if ( docItem.type() != null) {
							leganEulaArray.add(docItem);
						}
					}
				}
			}
		}
		
		ReferenceCodesUtils.printResult(leganEulaArray);
	}

}
