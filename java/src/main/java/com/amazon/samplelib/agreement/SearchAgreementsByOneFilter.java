//AG-02 AG-05
package com.amazon.samplelib.agreement;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AgreementViewSummary;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

/**
 * To search by offer id: OfferId;
 * by product id: ResourceIdentifier; 
 * by customer AWS account id: AcceptorAccountId
 * by product type: ResourceType (i.e. SaasProduct)
 * by status: Status. status values can be: 
 * 			ACTIVE, CANCELED, EXPIRED, RENEWED, REPLACED, ROLLED_BACK, SUPERSEDED, TERMINATED
 */

public class SearchAgreementsByOneFilter {
	
	static String idType = "ResourceType"; // Status
	
	static String idValue = "SaaSProduct"; // ACTIVE
	
	static String partyTypeFilterValue = ReferenceCodesConstants.PartyTypeFilterValueProposer;
	
	public static void main(String[] args) {
		
		List<AgreementViewSummary> agreementSummaryList = new ArrayList<AgreementViewSummary>();
		
		MarketplaceAgreementClient mpasClient = ReferenceCodesUtils.getMPAgreementClient();

		Map<String, String> filtersMap = new HashMap<>() {{
			put(idType, idValue);
		}};
		
		agreementSummaryList = ReferenceCodesUtils.getSearchAgreementSummaryList(mpasClient, ReferenceCodesUtils.getFilters(partyTypeFilterValue, filtersMap), null);
		
		ReferenceCodesUtils.printResult(agreementSummaryList);
	}
	

}
