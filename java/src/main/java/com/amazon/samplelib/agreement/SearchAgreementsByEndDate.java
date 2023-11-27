package com.amazon.samplelib.agreement;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AgreementViewSummary;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

public class SearchAgreementsByEndDate {
	
	static String beforeOrAfterEndtimeFilterName = ReferenceCodesConstants.BeforeOrAfterEndTimeFilterName.BeforeEndTime.name();
	
	static String cutoffDate = "2322-11-18T00:00:00Z";
	
	static String partyTypeFilterValue = ReferenceCodesConstants.PartyTypeFilterValueProposer;

	public static void main(String[] args) {
		
		List<AgreementViewSummary> agreementSummaryList = new ArrayList<AgreementViewSummary>();
		
		MarketplaceAgreementClient mpasClient = ReferenceCodesUtils.getMPAgreementClient();
		
		Map<String, String> filtersMap = new HashMap<>() {{
			put(beforeOrAfterEndtimeFilterName, cutoffDate);
		}};
				
		agreementSummaryList = ReferenceCodesUtils.getSearchAgreementSummaryList(mpasClient, ReferenceCodesUtils.getFilters(partyTypeFilterValue, filtersMap), null);
		
		ReferenceCodesUtils.printResult(agreementSummaryList);
	}
	

}
