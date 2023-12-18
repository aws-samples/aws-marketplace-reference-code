package com.example.awsmarketplace.agreementapi;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.*;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementResponse;

public class GetAgreementCustomerInfo {

	/*
	 * Obtain metadata about the customer who created the agreement, such as the customer's AWS Account ID
	 */
	public static void main(String[] args) {

		MarketplaceAgreementClient marketplaceAgreementClient = 
				MarketplaceAgreementClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();

		DescribeAgreementRequest describeAgreementRequest = 
				DescribeAgreementRequest.builder()
				.agreementId(AGREEMENT_ID)
				.build();

		DescribeAgreementResponse describeAgreementResponse = marketplaceAgreementClient.describeAgreement(describeAgreementRequest);

		System.out.println("Customer's AWS Account ID is " + describeAgreementResponse.acceptor().accountId());

	}

}
