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
		
		MarketplaceAgreementClient marketplaceAgreementClient = 
				MarketplaceAgreementClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();

		GetAgreementTermsRequest getAgreementTermsRequest = 
				GetAgreementTermsRequest.builder()
				.agreementId(AGREEMENT_ID)
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

		System.out.println("Auto-Renewal status is " + autoRenewal);
	}

}
