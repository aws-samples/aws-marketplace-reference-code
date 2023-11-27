//AG-02 AG-05
package com.amazon.samplelib.agreement;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AgreementViewSummary;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

/**
 * Party Type = Proposer AND Acceptor:
 * 		AfterEndTime
 * 		BeforeEndTime
 * 		ResourceIdentifier + BeforeEndTime
 * 		ResourceIdentifier + AfterEndTime
 * 		ResourceType + BeforeEndTime
 * 		ResourceType + AfterEndTime
 * Party Type = Proposer
 * 		ResourceIdentifier
 * 		OfferId
 * 		AcceptorAccountId 
 * 		Status (ACTIVE)
 * 		Status (ACTIVE) + ResourceIdentifier
 * 		Status (ACTIVE) + AcceptorAccountId
 * 		Status (ACTIVE) + OfferId
 * 		Status (ACTIVE) + ResourceType
 * 		AcceptorAccountId + BeforeEndTime
 * 		AcceptorAccountId + AfterEndTime
 * 		AcceptorAccountId + AfterEndTime
 * 		OfferId + BeforeEndTime
 * Status values can be: 
 * 			ACTIVE, CANCELED, EXPIRED, RENEWED, REPLACED, ROLLED_BACK, SUPERSEDED, TERMINATED
 */

public class SearchAgreementsByTwoFilters {
	
	static String filter1Type = "ResourceType"; // Status
	
	static String filter1Value = "SaaSProduct"; // ACTIVE
	
	static String filter2Type = "Status";
	
	static String filter2Value = "ACTIVE";
	
	static String partyTypeFilterValue = ReferenceCodesConstants.PartyTypeFilterValueProposer;

	public static void main(String[] args) {
		
		MarketplaceAgreementClient mpasClient = ReferenceCodesUtils.getMPAgreementClient();
		
		Map<String, String> filtersMap = new HashMap<>() {{
			put(filter1Type, filter1Value);
			put(filter2Type, filter2Value);
		}};
		
		List<AgreementViewSummary> agreementSummaryList = ReferenceCodesUtils.getSearchAgreementSummaryList(mpasClient, ReferenceCodesUtils.getFilters(partyTypeFilterValue, filtersMap), null);

		ReferenceCodesUtils.printResult(agreementSummaryList);
	}
	

}
