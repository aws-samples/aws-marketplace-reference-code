package com.amazon.samplelib.utils;

import com.fasterxml.jackson.annotation.PropertyAccessor;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.annotation.JsonAutoDetect.Visibility;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.SdkHttpClient;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.SearchAgreementsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.SearchAgreementsResponse;
import software.amazon.awssdk.services.marketplacecatalog.MarketplaceCatalogClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.AgreementViewSummary;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.Filter;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsResponse;

public class ReferenceCodesUtils {
	
	public static MarketplaceCatalogClient getMPCatalogClient() {
	
		AwsCredentialsProvider awsCredentials1 = ProfileCredentialsProvider.create();
		SdkHttpClient httpClient = ApacheHttpClient.builder().build();
		
		MarketplaceCatalogClient awsMarketplaceCatalog = MarketplaceCatalogClient.builder()
				.httpClient(httpClient)
				.credentialsProvider(awsCredentials1)
				.build();
		
		return awsMarketplaceCatalog;
	}
	
	
	public static MarketplaceAgreementClient getMPAgreementClient() {
		
		AwsCredentialsProvider awsCredentials1 = ProfileCredentialsProvider.create();
		SdkHttpClient httpClient = ApacheHttpClient.builder().build();

		// can leave out .region(Region.US_EAST_1) because it's set up in the credentials file
		
		MarketplaceAgreementClient awsMarketplaceAgreement = MarketplaceAgreementClient.builder()
				.httpClient(httpClient)
				.credentialsProvider(awsCredentials1)
				.build();
		
		return awsMarketplaceAgreement;
	}
	
	public static DescribeAgreementResponse getDescribeAgreementResult(MarketplaceAgreementClient mpasClient, String agreementId){
		
		DescribeAgreementRequest describeAgreementRequest = DescribeAgreementRequest.builder()
                .agreementId(agreementId)
                .build();

		DescribeAgreementResponse result = mpasClient.describeAgreement(describeAgreementRequest);
		
		return result;
	}
	
	public static SearchAgreementsResponse getSearchAgreementResults(MarketplaceAgreementClient mpasClient, List<Filter> searchFilters, String nextToken) {
						
		SearchAgreementsRequest searchAgreementsRequest = SearchAgreementsRequest.builder()
              .catalog(ReferenceCodesConstants.AWS_MP_CATALOG)
              .filters(searchFilters)
              .nextToken(nextToken)
              .build();
		SearchAgreementsResponse searchResult = mpasClient.searchAgreements(searchAgreementsRequest);
		
		return searchResult;

	}
	
	public static List<AgreementViewSummary> getSearchAgreementSummaryList(MarketplaceAgreementClient mpasClient, List<Filter> searchFilters, String nextToken) {
		
		List<AgreementViewSummary> agreementSummaryList = new ArrayList<AgreementViewSummary>();
		
		SearchAgreementsResponse searchResult = getSearchAgreementResults(mpasClient, searchFilters, nextToken);
		
		agreementSummaryList.addAll(searchResult.agreementViewSummaries());

		while (searchResult.nextToken() != null && searchResult.nextToken().length() > 0 ) {
			searchResult =  getSearchAgreementResults(mpasClient, searchFilters, searchResult.nextToken());;
			agreementSummaryList.addAll(searchResult.agreementViewSummaries());
		}
		
		return agreementSummaryList;

	}
	
	public static List<AcceptedTerm> getAgreementAcceptedTerms(MarketplaceAgreementClient mpasClient, String agreementId){
		
		GetAgreementTermsRequest agreementTermsRequest = GetAgreementTermsRequest.builder()
				.agreementId(agreementId)
				.build();

		GetAgreementTermsResponse result = mpasClient.getAgreementTerms(agreementTermsRequest);
		
		List<AcceptedTerm> acceptedTerms = result.acceptedTerms();
		
		return acceptedTerms;
	}
	
	public static GetAgreementTermsResponse getAgreementTerms(MarketplaceAgreementClient mpasClient, String agreementId){
		
		GetAgreementTermsRequest agreementTermsRequest = GetAgreementTermsRequest.builder()
				.agreementId(agreementId)
				.build();

		GetAgreementTermsResponse result = mpasClient.getAgreementTerms(agreementTermsRequest);
		
		return result;
	}

	public static List<Filter> getFilters(String partyTypeFilterValue, Map<String, String> filtersMap) {
		
		Filter partyType = Filter.builder()
                .name(ReferenceCodesConstants.PartyTypeFilterName)
                .values(partyTypeFilterValue)
                .build();
		
		Filter agreementType = Filter.builder()
                .name(ReferenceCodesConstants.AgreementTypeFilterName)
                .values(ReferenceCodesConstants.AgreementTypeFilterValuePurchaseAg)
                .build();
		
		List<Filter> filters = new ArrayList<Filter>();
		filters.add(partyType);
		filters.add(agreementType);
		
		for (Map.Entry<String, String> entry : filtersMap.entrySet()) {
			String key = entry.getKey();
            String value = entry.getValue();
            Filter newFilter = Filter.builder()
	                .name(key)
	                .values(value)
	                .build();
            filters.add(newFilter);
			System.out.println("Added filter : " + key + "=" + value);

		}

		return filters;
	}
	
	public static void printResult(Object result) {
		try {
			ObjectMapper om = new ObjectMapper();
			om.configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, false);
			om.setVisibility(PropertyAccessor.FIELD, Visibility.ANY);
			om.registerModule(new JavaTimeModule());
			ObjectWriter ow = om.writer().withDefaultPrettyPrinter();
			
			String json = ow.writeValueAsString(result);
			System.out.println(json);
		} catch (JsonProcessingException e) {
			e.printStackTrace();
		}
	}
}
