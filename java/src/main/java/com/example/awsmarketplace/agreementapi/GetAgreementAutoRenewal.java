// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.*;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsResponse;

public class GetAgreementAutoRenewal {

	/*
	 * Obtain the auto-renewal status of the agreement
	 */
	
	public static void main(String[] args) {
		
		String agreementId = args.length > 0 ? args[0] : AGREEMENT_ID;
		
		String autoRenewal = getAutoRenewal(agreementId);

		System.out.println("Auto-Renewal status is " + autoRenewal);
	}

	public static String getAutoRenewal(String agreementId) {
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

		String autoRenewal = "No Auto Renewal";

		for (AcceptedTerm acceptedTerm : getAgreementTermsResponse.acceptedTerms()) {
			if (acceptedTerm.renewalTerm() != null && acceptedTerm.renewalTerm().configuration() != null
					&& acceptedTerm.renewalTerm().configuration().enableAutoRenew() != null) {
				autoRenewal = String.valueOf(acceptedTerm.renewalTerm().configuration().enableAutoRenew().booleanValue());
				break;
			}
		}
		return autoRenewal;
	}

}
