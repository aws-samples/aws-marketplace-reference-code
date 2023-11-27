package com.amazon.samplelib.agreement;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AgreementViewSummary;
import software.amazon.awssdk.services.marketplaceagreement.model.Filter;

import java.util.ArrayList;
import java.util.List;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

public class GetAllAgreementsIds {

	public static void main(String[] args) {
		
		MarketplaceAgreementClient mpasClient = ReferenceCodesUtils.getMPAgreementClient();

		Filter partyType = Filter.builder()
                .name(ReferenceCodesConstants.PartyTypeFilterName)
                .values(ReferenceCodesConstants.PartyTypeFilterValueProposer)
                .build();
		
		Filter agreementType = Filter.builder()
                .name(ReferenceCodesConstants.AgreementTypeFilterName)
                .values(ReferenceCodesConstants.AgreementTypeFilterValuePurchaseAg)
                .build();
		
		List<AgreementViewSummary> agreementSummaryList = ReferenceCodesUtils.getSearchAgreementSummaryList(mpasClient, List.of(partyType, agreementType), null);
	
		List<String> agreementIds = new ArrayList<String>();
		for (AgreementViewSummary summary : agreementSummaryList) {
			agreementIds.add(summary.agreementId());
			System.out.println(summary.agreementId());
		}
		
	}
	

}
