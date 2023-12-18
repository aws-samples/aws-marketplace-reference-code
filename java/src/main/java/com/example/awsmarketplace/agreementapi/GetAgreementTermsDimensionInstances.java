package com.example.awsmarketplace.agreementapi;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.Dimension;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsResponse;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.AGREEMENT_ID;
import com.example.awsmarketplace.utils.ReferenceCodesUtils;

public class GetAgreementTermsDimensionInstances {

	/* 
	 * get instances of each dimension that buyer has purchased in the agreement
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

		Map<String, List<Dimension>> dimensionMap = new HashMap<String, List<Dimension>>();

		for (AcceptedTerm acceptedTerm : getAgreementTermsResponse.acceptedTerms()) {
			List<Dimension> dimensionsList = new ArrayList<Dimension>();
			if (acceptedTerm.configurableUpfrontPricingTerm() != null) {
				String selectorValue = "";
				if (acceptedTerm.configurableUpfrontPricingTerm().configuration() != null) {
					if (acceptedTerm.configurableUpfrontPricingTerm().configuration().selectorValue() != null) {
						selectorValue = acceptedTerm.configurableUpfrontPricingTerm().configuration().selectorValue();
					}
					if (acceptedTerm.configurableUpfrontPricingTerm().configuration().hasDimensions()) {
						dimensionsList = acceptedTerm.configurableUpfrontPricingTerm().configuration().dimensions();
					}
				}
				if (selectorValue.length() > 0) {
					dimensionMap.put(selectorValue, dimensionsList);
				}
			}
		}

		ReferenceCodesUtils.formatOutput(dimensionMap);
	}
}
