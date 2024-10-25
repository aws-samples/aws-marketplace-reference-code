// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.*;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementResponse;

public class GetAgreementFinancialDetails {

	/*
	 * Obtain financial details, such as Total Contract Value of the agreement from a given agreement
	 */
	public static void main(String[] args) {

		String agreementId = args.length > 0 ? args[0] : AGREEMENT_ID;

		String totalContractValue = getTotalContractValue(agreementId);

		System.out.println("Total Contract Value is " + totalContractValue);

	}

	public static String getTotalContractValue(String agreementId) {
		MarketplaceAgreementClient marketplaceAgreementClient = 
				MarketplaceAgreementClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();

		DescribeAgreementRequest describeAgreementRequest = 
				DescribeAgreementRequest.builder()
				.agreementId(agreementId)
				.build();

		DescribeAgreementResponse describeAgreementResponse = marketplaceAgreementClient.describeAgreement(describeAgreementRequest);
		
		String totalContractValue = "N/A";

		if ( describeAgreementResponse.estimatedCharges() != null ) {
			totalContractValue = describeAgreementResponse.estimatedCharges().agreementValue() 
					+ " " 
					+ describeAgreementResponse.estimatedCharges().currencyCode();
		}
		return totalContractValue;
	}
}
