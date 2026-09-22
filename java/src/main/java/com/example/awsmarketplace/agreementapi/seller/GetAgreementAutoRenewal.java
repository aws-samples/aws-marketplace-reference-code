// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi.seller;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.*;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.EndTimeBehavior;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.PaymentScheduleEntry;
import software.amazon.awssdk.services.marketplaceagreement.model.PriceIncrease;
import software.amazon.awssdk.services.marketplaceagreement.model.RenewalTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.TermTemplate;

public class GetAgreementAutoRenewal {

	/*
	 * Obtain the auto-renewal status of the agreement
	 */

	public static void main(String[] args) {

		String agreementId = args.length > 0 ? args[0] : AGREEMENT_ID;

		RenewalTerm renewalTerm = getRenewalTerm(agreementId);

		printRenewalTerm(renewalTerm);

		printEndTimeBehavior(agreementId);
	}

	/*
	 * Returns whether the agreement is set to auto renew, or "No Auto Renewal" when there is no
	 * renewal term or the flag is not set. Delegates to getRenewalTerm so there is a single API path.
	 */
	public static String getAutoRenewal(String agreementId) {

		RenewalTerm renewalTerm = getRenewalTerm(agreementId);

		if (renewalTerm != null && renewalTerm.configuration() != null
				&& renewalTerm.configuration().enableAutoRenew() != null) {
			return String.valueOf(renewalTerm.configuration().enableAutoRenew().booleanValue());
		}
		return "No Auto Renewal";
	}

	/*
	 * Reads the agreement's renewal term. These values come from the offer and are read-only here.
	 * Returns the first renewal term found, or null when the agreement has none.
	 */
	public static RenewalTerm getRenewalTerm(String agreementId) {

		MarketplaceAgreementClient marketplaceAgreementClient =
				MarketplaceAgreementClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();

		String nextToken = null;

		do {
			GetAgreementTermsResponse getAgreementTermsResponse =
					marketplaceAgreementClient.getAgreementTerms(
							GetAgreementTermsRequest.builder()
							.agreementId(agreementId)
							.nextToken(nextToken)
							.build());

			for (AcceptedTerm acceptedTerm : getAgreementTermsResponse.acceptedTerms()) {
				// AcceptedTerm is a union. Only the renewal term is of interest here.
				if (acceptedTerm.renewalTerm() != null) {
					return acceptedTerm.renewalTerm();
				}
			}

			nextToken = getAgreementTermsResponse.nextToken();
		} while (nextToken != null);

		return null;
	}

	/*
	 * Prints the fields of a renewal term.
	 */
	public static void printRenewalTerm(RenewalTerm renewalTerm) {

		if (renewalTerm == null) {
			System.out.println("No Auto Renewal");
			return;
		}

		System.out.println("Renewal Term ID: " + renewalTerm.id());

		if (renewalTerm.configuration() != null) {
			System.out.println("Auto Renew Enabled: " + renewalTerm.configuration().enableAutoRenew());
		}

		// ISO 8601 duration. The customer can no longer change enableAutoRenew once the
		// agreement is within this duration of its end date. Absent when the offer sets no deadline,
		// which leaves the customer free to change enableAutoRenew up to the end date.
		if (renewalTerm.lockoutPeriod() != null) {
			System.out.println("Lockout Period: " + renewalTerm.lockoutPeriod());
		} else {
			System.out.println("Lockout Period: none");
		}

		// Absent means the agreement can renew without limit.
		if (renewalTerm.maxRenewals() != null) {
			System.out.println("Max Renewals: " + renewalTerm.maxRenewals());
		} else {
			System.out.println("Max Renewals: unlimited");
		}

		// Absent unless the offer sets a separate deadline for adjusting the renewal price.
		if (renewalTerm.adjustmentDeadline() != null) {
			System.out.println("Adjustment Deadline: " + renewalTerm.adjustmentDeadline());
		}

		printPriceIncrease(renewalTerm.priceIncrease());

		for (TermTemplate termTemplate : renewalTerm.termTemplates()) {
			printTermTemplate(termTemplate);
		}
	}

	/*
	 * Reads the price change that applies when the agreement renews.
	 */
	public static void printPriceIncrease(PriceIncrease priceIncrease) {

		if (priceIncrease == null) {
			System.out.println("Price Increase: none (the price does not change at renewal)");
			return;
		}

		// PriceIncrease is a union. Exactly one variant is set.
		if (priceIncrease.fixedPercentage() != null) {
			System.out.println("Fixed Price Increase Percentage: " + priceIncrease.fixedPercentage().value());
		} else if (priceIncrease.percentageRange() != null) {
			// The uplift is open within this range; defaultValue applies if you take no action.
			System.out.println("Price Increase Min Percentage: " + priceIncrease.percentageRange().minValue());
			System.out.println("Price Increase Max Percentage: " + priceIncrease.percentageRange().maxValue());
			System.out.println("Price Increase Default Percentage: " + priceIncrease.percentageRange().defaultValue());
		}
	}

	/*
	 * Reads the term template that applies when the agreement renews.
	 */
	public static void printTermTemplate(TermTemplate termTemplate) {

		// TermTemplate is a union. Only payment schedule templates are supported today.
		if (termTemplate.paymentScheduleTermTemplate() == null) {
			System.out.println("Term Template: not a payment schedule template");
			return;
		}

		System.out.println("Payment Schedule Template:");
		for (PaymentScheduleEntry entry : termTemplate.paymentScheduleTermTemplate().schedule()) {
			// chargeDateOffset is relative to the start of the renewed agreement, e.g. "P3M".
			String line = "  Charge Date Offset: " + entry.chargeDateOffset()
					+ ", Charge Percentage: " + entry.chargePercentage();

			// Absent unless the schedule pins charges to a day of the month.
			if (entry.dayOfMonth() != null) {
				line += ", Day Of Month: " + entry.dayOfMonth();
			}

			System.out.println(line);
		}
	}

	/*
	 * Reads the agreement's end time behavior: whether it will renew, be replaced, or expire, and why.
	 */
	public static void printEndTimeBehavior(String agreementId) {

		MarketplaceAgreementClient marketplaceAgreementClient =
				MarketplaceAgreementClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();

		DescribeAgreementResponse describeAgreementResponse =
				marketplaceAgreementClient.describeAgreement(
						DescribeAgreementRequest.builder().agreementId(agreementId).build());

		EndTimeBehavior endTimeBehavior = describeAgreementResponse.endTimeBehavior();
		if (endTimeBehavior == null) {
			System.out.println("End Time Behavior: none (this agreement has no end date)");
			return;
		}

		System.out.println("End Time Behavior Type: " + endTimeBehavior.typeAsString());

		// The reason the agreement does not renew, and absent when it does. My own PROPOSER_RENEW_OPTED_OUT
		// leaves enableAutoRenew untouched, so the flag can read true even when this says it will not renew.
		if (endTimeBehavior.reasonCodeAsString() != null) {
			System.out.println("End Time Behavior Reason Code: " + endTimeBehavior.reasonCodeAsString());
		}

		// renewalSummary is present whenever type is RENEW, but offerId inside it is absent
		// until a renewal offer is created.
		if (endTimeBehavior.renewalSummary() != null && endTimeBehavior.renewalSummary().offerId() != null) {
			System.out.println("Renewal Offer ID: " + endTimeBehavior.renewalSummary().offerId());
		}
	}

}
