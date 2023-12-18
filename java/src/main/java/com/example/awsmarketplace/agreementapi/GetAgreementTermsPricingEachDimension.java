package com.example.awsmarketplace.agreementapi;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsResponse;

import java.util.ArrayList;
import java.util.List;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.AGREEMENT_ID;
import com.example.awsmarketplace.utils.ReferenceCodesUtils;

public class GetAgreementTermsPricingEachDimension {

	/*
	 * Obtain pricing per each dimension in the agreement
	 */
	public static void main(String[] args) {

		MarketplaceAgreementClient marketplaceAgreementClient = 
				MarketplaceAgreementClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();

		GetAgreementTermsRequest getAgreementTermsRequest = 
				GetAgreementTermsRequest.builder().agreementId(AGREEMENT_ID)
				.build();

		GetAgreementTermsResponse getAgreementTermsResponse = marketplaceAgreementClient.getAgreementTerms(getAgreementTermsRequest);

		List<Object> dimensions = new ArrayList<Object>();

		for (AcceptedTerm acceptedTerm : getAgreementTermsResponse.acceptedTerms()) {
			List<Object> rateInfo = new ArrayList<Object>();
			if (acceptedTerm.configurableUpfrontPricingTerm() != null) {
				if (acceptedTerm.configurableUpfrontPricingTerm().type() != null) {
					rateInfo.add(acceptedTerm.configurableUpfrontPricingTerm().type());
				}
				if (acceptedTerm.configurableUpfrontPricingTerm().currencyCode() != null) {
					rateInfo.add(acceptedTerm.configurableUpfrontPricingTerm().currencyCode());
				}
				if (acceptedTerm.configurableUpfrontPricingTerm().hasRateCards()) {
					rateInfo.add(acceptedTerm.configurableUpfrontPricingTerm().rateCards());
				}
				dimensions.add(rateInfo);
			}
		}

		ReferenceCodesUtils.formatOutput(dimensions);
	}
}
