package com.example.awsmarketplace.agreementapi;

import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.SdkHttpClient;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AgreementViewSummary;
import software.amazon.awssdk.services.marketplaceagreement.model.Filter;
import software.amazon.awssdk.services.marketplaceagreement.model.SearchAgreementsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.SearchAgreementsResponse;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.*;
import com.example.awsmarketplace.utils.ReferenceCodesUtils;

/**
 * Party Type = Proposer AND Acceptor: 
 * 	AfterEndTime 
 * 	BeforeEndTime
 * 	ResourceIdentifier + BeforeEndTime 
 * 	ResourceIdentifier + AfterEndTime
 * 	ResourceType + BeforeEndTime 
 * 	ResourceType + AfterEndTime 
 * 
 * Party Type = Proposer 
 * 	ResourceIdentifier 
 * 	OfferId 
 * 	AcceptorAccountId 
 * 	Status (ACTIVE) 
 * 	Status (ACTIVE) + ResourceIdentifier 
 * 	Status (ACTIVE) + AcceptorAccountId 
 * 	Status (ACTIVE) + OfferId 
 * 	Status (ACTIVE) + ResourceType 
 * 	AcceptorAccountId + BeforeEndTime 
 * 	AcceptorAccountId + AfterEndTime 
 * 	AcceptorAccountId + AfterEndTime 
 * 	OfferId + BeforeEndTime 
 * 
 * Status values can be: ACTIVE, CANCELLED, EXPIRED, RENEWED, REPLACED, ROLLED_BACK, SUPERSEDED, TERMINATED
 */

public class SearchAgreementsByTwoFilters {

	public static final String FILTER_1_NAME = "ResourceType";

	public static final String FILTER_1_VALUE = "SaaSProduct";

	public static final String FILTER_2_NAME = "Status";

	public static final String FILTER_2_VALUE = "ACTIVE";
	
	/*
	 * search agreements by two customize filter
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
		
		Filter customizeFilter1 = Filter.builder().name(FILTER_1_NAME).values(FILTER_1_VALUE).build();
		
		Filter customizeFilter2 = Filter.builder().name(FILTER_2_NAME).values(FILTER_2_VALUE).build();

		
		List<Filter> filters = new ArrayList<Filter>();
		
		filters.addAll(Arrays.asList(partyTypeFilter, agreementTypeFilter, customizeFilter1, customizeFilter2));
		
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
