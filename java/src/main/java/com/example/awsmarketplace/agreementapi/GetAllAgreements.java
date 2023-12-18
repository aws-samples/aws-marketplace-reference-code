package com.example.awsmarketplace.agreementapi;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
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

public class GetAllAgreements {

	/*
	 * Get all purchase agreements with party type = proposer; 
	 * Depend on the number of agreements in your account, this code may take some time to finish.
	 */
	public static void main(String[] args) {

		MarketplaceAgreementClient marketplaceAgreementClient = 
				MarketplaceAgreementClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();
		
		// get all filters
		
		Filter partyType = Filter.builder().name(PARTY_TYPE_FILTER_NAME)
				.values(PARTY_TYPE_FILTER_VALUE_PROPOSER).build();

		Filter agreementType = Filter.builder().name(AGREEMENT_TYPE_FILTER_NAME)
				.values(AGREEMENT_TYPE_FILTER_VALUE_PURCHASEAGREEMENT).build();
		
		List<Filter> searchFilters = new ArrayList<Filter>();
		
		searchFilters.addAll(Arrays.asList(partyType, agreementType));
		
		// Save all results in a list array

		List<AgreementViewSummary> agreementSummaryList = new ArrayList<AgreementViewSummary>();

		SearchAgreementsRequest searchAgreementsRequest = 
				SearchAgreementsRequest.builder()
				.catalog(AWS_MP_CATALOG)
				.filters(searchFilters)
				.build();
		
		SearchAgreementsResponse searchAgreementsResponse = marketplaceAgreementClient.searchAgreements(searchAgreementsRequest);

		agreementSummaryList.addAll(searchAgreementsResponse.agreementViewSummaries());

		while (searchAgreementsResponse.nextToken() != null && searchAgreementsResponse.nextToken().length() > 0) {
			searchAgreementsRequest = 
					SearchAgreementsRequest.builder()
					.catalog(AWS_MP_CATALOG)
					.nextToken(searchAgreementsResponse.nextToken())
					.filters(searchFilters).build();
			searchAgreementsResponse = marketplaceAgreementClient.searchAgreements(searchAgreementsRequest);
			agreementSummaryList.addAll(searchAgreementsResponse.agreementViewSummaries());
		}

		ReferenceCodesUtils.formatOutput(agreementSummaryList);
	}

}
