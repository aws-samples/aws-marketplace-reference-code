// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.DocumentItem;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsResponse;

import java.util.ArrayList;
import java.util.List;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.AGREEMENT_ID;
import com.example.awsmarketplace.utils.ReferenceCodesUtils;

public class GetAgreementTermsEula {

	/*
	 * Obtain the EULA I have entered into with my customer via the agreement
	 */
	public static void main(String[] args) {

		String agreementId = args.length > 0 ? args[0] : AGREEMENT_ID;

		List<DocumentItem> legalEulaArray = getLegalEula(agreementId);
		
		ReferenceCodesUtils.formatOutput(legalEulaArray);
	}

	public static List<DocumentItem> getLegalEula(String agreementId) {
		MarketplaceAgreementClient marketplaceAgreementClient = 
				MarketplaceAgreementClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();

		GetAgreementTermsRequest getAgreementTermsRequest = 
				GetAgreementTermsRequest.builder().agreementId(agreementId)
				.build();

		GetAgreementTermsResponse getAgreementTermsResponse = marketplaceAgreementClient.getAgreementTerms(getAgreementTermsRequest);

		List<DocumentItem> legalEulaArray = new ArrayList<>();

		getAgreementTermsResponse.acceptedTerms().stream()
	    	.filter(acceptedTerm -> acceptedTerm.legalTerm() != null && acceptedTerm.legalTerm().hasDocuments())
	    	.flatMap(acceptedTerm -> acceptedTerm.legalTerm().documents().stream())
	    	.filter(docItem -> docItem.type() != null)
	    	.forEach(legalEulaArray::add);
		return legalEulaArray;
	}

}
