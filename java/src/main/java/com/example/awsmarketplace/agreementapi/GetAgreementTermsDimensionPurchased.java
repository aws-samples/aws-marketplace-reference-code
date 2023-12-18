package com.example.awsmarketplace.agreementapi;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.Dimension;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsResponse;

import java.util.ArrayList;
import java.util.List;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.AGREEMENT_ID;
import com.example.awsmarketplace.utils.ReferenceCodesUtils;

public class GetAgreementTermsDimensionPurchased {

	/*
	 * Obtain the dimensions the buyer has purchased from me via the agreement
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

		List<String> dimensionKeys = new ArrayList<String>();
		for (AcceptedTerm acceptedTerm : getAgreementTermsResponse.acceptedTerms()) {
			if (acceptedTerm.configurableUpfrontPricingTerm() != null) {
				if (acceptedTerm.configurableUpfrontPricingTerm().configuration().selectorValue() != null) {
					List<Dimension> dimensions = acceptedTerm.configurableUpfrontPricingTerm().configuration().dimensions();
					for (Dimension dimension : dimensions) {
						dimensionKeys.add(dimension.dimensionKey());
					}
				}

			}
		}

		ReferenceCodesUtils.formatOutput(dimensionKeys);
	}
}
