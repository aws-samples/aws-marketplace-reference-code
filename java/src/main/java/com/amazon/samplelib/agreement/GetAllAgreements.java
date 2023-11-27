package com.amazon.samplelib.agreement;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AgreementViewSummary;
import software.amazon.awssdk.services.marketplaceagreement.model.Filter;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

import java.util.List;

public class GetAllAgreements {

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
		
		ReferenceCodesUtils.printResult(agreementSummaryList);
	}
	

}
