// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.FreeTrialPricingTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsResponse;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.AGREEMENT_ID;

import java.util.ArrayList;
import java.util.List;

import com.example.awsmarketplace.utils.ReferenceCodesUtils;

public class GetAgreementTermsFreeTrialDetails {

	/*
	 * Obtain the details from an agreement of a free trial I have provided to the customer
	 */
	public static void main(String[] args) {

		String agreementId = args.length > 0 ? args[0] : AGREEMENT_ID;
		
		List<FreeTrialPricingTerm> freeTrialPricingTerms = getFreeTrialPricingTerms(agreementId);

		ReferenceCodesUtils.formatOutput(freeTrialPricingTerms);
	}

	public static List<FreeTrialPricingTerm> getFreeTrialPricingTerms(String agreementId) {
		MarketplaceAgreementClient marketplaceAgreementClient = 
				MarketplaceAgreementClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();

		GetAgreementTermsRequest getAgreementTermsRequest = 
				GetAgreementTermsRequest.builder().agreementId(agreementId)
					.build();

		GetAgreementTermsResponse getAgreementTermsResponse = marketplaceAgreementClient.getAgreementTerms(getAgreementTermsRequest);

		List<FreeTrialPricingTerm> freeTrialPricingTerms = new ArrayList<FreeTrialPricingTerm>();

		for (AcceptedTerm acceptedTerm : getAgreementTermsResponse.acceptedTerms()) {
			if (acceptedTerm.freeTrialPricingTerm() != null) {
				freeTrialPricingTerms.add(acceptedTerm.freeTrialPricingTerm());
			}
		}
		return freeTrialPricingTerms;
	}
}
