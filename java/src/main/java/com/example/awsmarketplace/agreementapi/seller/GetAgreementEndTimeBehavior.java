// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi.seller;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.*;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.EndTimeBehavior;

public class GetAgreementEndTimeBehavior {

	/*
	 * Find out whether the agreement will renew, be replaced, or expire at its end date, and why
	 */

	public static void main(String[] args) {

		String agreementId = args.length > 0 ? args[0] : AGREEMENT_ID;

		EndTimeBehavior endTimeBehavior = getEndTimeBehavior(agreementId);

		// endTimeBehavior is absent for agreements that have no end date, such as pay-as-you-go.
		if (endTimeBehavior == null) {
			System.out.println("Agreement " + agreementId + " has no end date, so it has no end time behavior.");
			return;
		}

		System.out.println("End time behavior is " + endTimeBehavior.typeAsString());

		// reasonCode is null when type is RENEW, otherwise the reason the agreement does not renew.
		if (endTimeBehavior.reasonCodeAsString() != null) {
			System.out.println("Reason is " + endTimeBehavior.reasonCodeAsString());
		}

		// renewalSummary is present whenever type is RENEW, but offerId inside it is absent
		// until a renewal offer is created.
		if (endTimeBehavior.renewalSummary() != null && endTimeBehavior.renewalSummary().offerId() != null) {
			System.out.println("Next renewal will use offer " + endTimeBehavior.renewalSummary().offerId());
		}
	}

	public static EndTimeBehavior getEndTimeBehavior(String agreementId) {

		MarketplaceAgreementClient marketplaceAgreementClient =
				MarketplaceAgreementClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();

		DescribeAgreementRequest describeAgreementRequest =
				DescribeAgreementRequest.builder()
				.agreementId(agreementId)
				.build();

		DescribeAgreementResponse describeAgreementResponse =
				marketplaceAgreementClient.describeAgreement(describeAgreementRequest);

		return describeAgreementResponse.endTimeBehavior();
	}

}
