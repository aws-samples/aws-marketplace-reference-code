// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi.seller;

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

/**
 * This filter is supported only when PartyType is Proposer, so only sellers can use it. An
 * unsupported combination fails with a ValidationException whose reason is UNSUPPORTED_FILTERS.
 * All filter combinations we support for Proposer and Acceptor:
 * https://docs.aws.amazon.com/marketplace/latest/APIReference/API_marketplace-agreements_SearchAgreements.html
 */

public class SearchAgreementsByStartDate {

	// change to AfterStartTime if after start time is desired
	static String beforeOrAfterStartTimeFilterName = BeforeOrAfterStartTimeFilterName.BeforeStartTime.name();

	static String cutoffDate = "2050-11-18T00:00:00Z";

	static String partyTypeFilterValue = PARTY_TYPE_FILTER_VALUE_PROPOSER;

	public static void main(String[] args) {

		List<AgreementViewSummary> agreementSummaryList = getAgreements();

		ReferenceCodesUtils.formatOutput(agreementSummaryList);
	}

	public static List<AgreementViewSummary> getAgreements() {
		MarketplaceAgreementClient marketplaceAgreementClient =
				MarketplaceAgreementClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();

		// This filter is supported only for the proposer, so leave PartyType set to
		// PARTY_TYPE_FILTER_VALUE_PROPOSER. PARTY_TYPE_FILTER_VALUE_ACCEPTOR fails with a
		// ValidationException whose reason is UNSUPPORTED_FILTERS.
		Filter partyTypeFilter = Filter.builder().name(PARTY_TYPE_FILTER_NAME)
				.values(partyTypeFilterValue).build();

		Filter agreementTypeFilter = Filter.builder().name(AGREEMENT_TYPE_FILTER_NAME)
				.values(AGREEMENT_TYPE_FILTER_VALUE_PURCHASEAGREEMENT).build();

		Filter customizeFilter = Filter.builder().name(beforeOrAfterStartTimeFilterName).values(cutoffDate).build();

		List<Filter> filters = new ArrayList<Filter>();

		filters.addAll(Arrays.asList(partyTypeFilter, agreementTypeFilter, customizeFilter));

		// search agreement with filters

		SearchAgreementsRequest searchAgreementsRequest =
				SearchAgreementsRequest.builder()
				.catalog(AWS_MP_CATALOG)
				.filters(filters)
				.build();

		SearchAgreementsResponse searchAgreementResponse = marketplaceAgreementClient.searchAgreements(searchAgreementsRequest);

		List<AgreementViewSummary> agreementSummaryList = new ArrayList<AgreementViewSummary>();

		agreementSummaryList.addAll(searchAgreementResponse.agreementViewSummaries());

		while (searchAgreementResponse.nextToken() != null && searchAgreementResponse.nextToken().length() > 0) {
			searchAgreementsRequest =
					SearchAgreementsRequest.builder()
					.catalog(AWS_MP_CATALOG)
					.filters(filters)
					.nextToken(searchAgreementResponse.nextToken())
					.build();
			searchAgreementResponse = marketplaceAgreementClient.searchAgreements(searchAgreementsRequest);
			agreementSummaryList.addAll(searchAgreementResponse.agreementViewSummaries());
		}
		return agreementSummaryList;
	}

}
