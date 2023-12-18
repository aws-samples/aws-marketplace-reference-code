package com.example.awsmarketplace.agreementapi;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AgreementViewSummary;
import software.amazon.awssdk.services.marketplaceagreement.model.Filter;
import software.amazon.awssdk.services.marketplaceagreement.model.SearchAgreementsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.SearchAgreementsResponse;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import com.example.awsmarketplace.utils.ReferenceCodesUtils;

/**
 * To search by 
 * offer id: OfferId; 
 * product id: ResourceIdentifier; 
 * customer AWS account id: AcceptorAccountId 
 * product type: ResourceType (i.e. SaasProduct)
 * status: Status. status values can be: ACTIVE, CANCELED,
 * 		EXPIRED, RENEWED, REPLACED, ROLLED_BACK, SUPERSEDED, TERMINATED
 */

public class SearchAgreementsByOneFilter {

	private static final String FILTER_NAME = "ResourceType"; 

	private static final String FILTER_VALUE = "SaaSProduct";

	/*
	 * search agreements by one customize filter
	 */
	public static void main(String[] args) {

		MarketplaceAgreementClient marketplaceAgreementClient = 
				MarketplaceAgreementClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();
		
		Filter partyTypeFilter = Filter.builder().name(PARTY_TYPE_FILTER_NAME)
				.values(PARTY_TYPE_FILTER_VALUE_PROPOSER).build();

		Filter agreementTypeFilter = Filter.builder().name(AGREEMENT_TYPE_FILTER_NAME)
				.values(AGREEMENT_TYPE_FILTER_VALUE_PURCHASEAGREEMENT).build();
		
		Filter customizeFilter = Filter.builder().name(FILTER_NAME).values(FILTER_VALUE).build();
		
		List<Filter> filters = new ArrayList<Filter>();
		
		filters.addAll(Arrays.asList(partyTypeFilter, agreementTypeFilter, customizeFilter));
		
		SearchAgreementsRequest searchAgreementsRequest = 
				SearchAgreementsRequest.builder()
				.catalog(AWS_MP_CATALOG)
				.filters(filters)
				.build();
		SearchAgreementsResponse searchAgreementsResponse = marketplaceAgreementClient.searchAgreements(searchAgreementsRequest);
		
		List<AgreementViewSummary> agreementSummaryList = new ArrayList<AgreementViewSummary>();

		agreementSummaryList.addAll(searchAgreementsResponse.agreementViewSummaries());

		while (searchAgreementsResponse.nextToken() != null && searchAgreementsResponse.nextToken().length() > 0) {
			searchAgreementsRequest = 
					SearchAgreementsRequest.builder()
					.catalog(AWS_MP_CATALOG)
					.filters(filters)
					.nextToken(searchAgreementsResponse.nextToken())
					.build();
			searchAgreementsResponse = marketplaceAgreementClient.searchAgreements(searchAgreementsRequest);
			agreementSummaryList.addAll(searchAgreementsResponse.agreementViewSummaries());
		}

		ReferenceCodesUtils.formatOutput(agreementSummaryList);
	}

}
