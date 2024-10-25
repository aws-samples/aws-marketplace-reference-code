// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.PaymentScheduleTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.ScheduleItem;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.*;
import com.example.awsmarketplace.utils.ReferenceCodesUtils;

public class GetAgreementTermsPaymentSchedule {

	/*
	 * Obtain the payment schedule I have agreed to with the agreement, including the invoice date and invoice amount
	 */
	public static void main(String[] args) {
		
		String agreementId = args.length > 0 ? args[0] : AGREEMENT_ID;

		List<Map<String, Object>> paymentScheduleArray = getPaymentSchedules(agreementId);

		ReferenceCodesUtils.formatOutput(paymentScheduleArray);
	}

	public static List<Map<String, Object>> getPaymentSchedules(String agreementId) {
		MarketplaceAgreementClient marketplaceAgreementClient = 
				MarketplaceAgreementClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();

		GetAgreementTermsRequest getAgreementTermsRequest = 
				GetAgreementTermsRequest.builder().agreementId(agreementId)
				.build();

		GetAgreementTermsResponse getAgreementTermsResponse = marketplaceAgreementClient.getAgreementTerms(getAgreementTermsRequest);
		List<Map<String, Object>> paymentScheduleArray = new ArrayList<>();

		String currencyCode = "";

		for (AcceptedTerm acceptedTerm : getAgreementTermsResponse.acceptedTerms()) {
			if (acceptedTerm.paymentScheduleTerm() != null) {
				PaymentScheduleTerm paymentScheduleTerm = acceptedTerm.paymentScheduleTerm();
				if (paymentScheduleTerm.currencyCode() != null) {
					currencyCode = paymentScheduleTerm.currencyCode();
				}
				if (paymentScheduleTerm.hasSchedule()) {
					for (ScheduleItem schedule : paymentScheduleTerm.schedule()) {
						if (schedule.chargeDate() != null) {
							String chargeDate = schedule.chargeDate().toString();
							String chargeAmount = schedule.chargeAmount();
							Map<String, Object> scheduleMap = new HashMap<>();
							scheduleMap.put(ATTRIBUTE_CURRENCY_CODE, currencyCode);
							scheduleMap.put(ATTRIBUTE_CHARGE_DATE, chargeDate);
							scheduleMap.put(ATTRIBUTE_CHARGE_AMOUNT, chargeAmount);
							paymentScheduleArray.add(scheduleMap);
						}
					}
				}
			}
		}
		return paymentScheduleArray;
	}
}
