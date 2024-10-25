// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.*;
import com.example.awsmarketplace.utils.ReferenceCodesUtils;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsResponse;

public class GetAgreementTerms {

	public static void main(String[] args) {

		String agreementId = args.length > 0 ? args[0] : AGREEMENT_ID;

		GetAgreementTermsResponse getAgreementTermsResponse = getAgreementTermsResponse(agreementId);

		ReferenceCodesUtils.formatOutput(getAgreementTermsResponse);

	}

	public static GetAgreementTermsResponse getAgreementTermsResponse(String agreementId) {
		MarketplaceAgreementClient marketplaceAgreementClient = 
				MarketplaceAgreementClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();

		GetAgreementTermsRequest getAgreementTermsRequest = 
				GetAgreementTermsRequest.builder()
				.agreementId(agreementId)
				.build();

		GetAgreementTermsResponse getAgreementTermsResponse = marketplaceAgreementClient.getAgreementTerms(getAgreementTermsRequest);
		return getAgreementTermsResponse;
	}

}
