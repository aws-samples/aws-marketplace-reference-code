// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.example.awsmarketplace.agreementapi.buyer.utils;

import com.fasterxml.jackson.annotation.JsonAutoDetect;
import com.fasterxml.jackson.annotation.PropertyAccessor;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.MapperFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import com.fasterxml.jackson.databind.SerializationFeature;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.EndTimeBehavior;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementEntitlementsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementEntitlementsResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.PaymentScheduleEntry;
import software.amazon.awssdk.services.marketplaceagreement.model.PriceIncrease;
import software.amazon.awssdk.services.marketplaceagreement.model.RenewalTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.TermTemplate;

import java.time.Duration;
import java.time.Instant;
import java.util.UUID;

public final class AgreementApiUtils {

    private AgreementApiUtils() {
    }

    public static void formatOutput(Object result) {
        try {
            ObjectMapper om = new ObjectMapper();
            om.configure(MapperFeature.REQUIRE_HANDLERS_FOR_JAVA8_TIMES, false);
            om.configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, false);
            om.setVisibility(PropertyAccessor.FIELD, JsonAutoDetect.Visibility.ANY);
            ObjectWriter ow = om.writer().withDefaultPrettyPrinter();

            String json = ow.writeValueAsString(result);
            System.out.println(json);
        } catch (JsonProcessingException e) {
            e.printStackTrace();
        }
    }

    public static String generateClientToken() {
        return UUID.randomUUID().toString();
    }

    public static GetAgreementEntitlementsResponse pollUntilEntitlementsAvailable(
            MarketplaceAgreementClient client, String agreementId) {
        GetAgreementEntitlementsRequest getEntitlementsRequest =
                GetAgreementEntitlementsRequest.builder().agreementId(agreementId).build();

        final Duration timeout = Duration.ofMinutes(15);
        final Duration initialBackoff = Duration.ofSeconds(2);
        final Duration maxBackoff = Duration.ofSeconds(60);

        Instant pollDeadline = Instant.now().plus(timeout);
        Duration currentBackoff = initialBackoff;

        while (true) {
            GetAgreementEntitlementsResponse entitlementsResponse =
                    client.getAgreementEntitlements(getEntitlementsRequest);
            boolean allEntitlementsActive = entitlementsResponse.agreementEntitlements().stream()
                    .noneMatch(entitlement -> "PENDING".equals(entitlement.statusAsString()));
            if (allEntitlementsActive) {
                return entitlementsResponse;
            }
            if (Instant.now().plus(currentBackoff).isAfter(pollDeadline)) {
                throw new RuntimeException(
                        "Entitlements still pending after 15 minutes for agreementId: " + agreementId);
            }
            System.out.printf("Entitlements not yet active. Retrying in %d seconds...%n",
                    currentBackoff.getSeconds());
            try {
                Thread.sleep(currentBackoff.toMillis());
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new RuntimeException("Interrupted while waiting for entitlements to become active", e);
            }
            currentBackoff = currentBackoff.multipliedBy(2).compareTo(maxBackoff) < 0
                    ? currentBackoff.multipliedBy(2)
                    : maxBackoff;
        }
    }

    /**
     * Prints the renewal term that the proposer set on the offer.
     */
    public static void printRenewalTerm(MarketplaceAgreementClient client, String agreementId) {
        String nextToken = null;

        do {
            GetAgreementTermsResponse response = client.getAgreementTerms(
                    GetAgreementTermsRequest.builder()
                            .agreementId(agreementId)
                            .nextToken(nextToken)
                            .build());

            for (AcceptedTerm acceptedTerm : response.acceptedTerms()) {
                if (acceptedTerm.renewalTerm() == null) {
                    continue;
                }
                RenewalTerm renewalTerm = acceptedTerm.renewalTerm();

                System.out.println("Renewal Term ID: " + renewalTerm.id());

                if (renewalTerm.configuration() != null) {
                    System.out.println("Auto Renew Enabled: "
                                               + renewalTerm.configuration().enableAutoRenew());
                }

                if (renewalTerm.lockoutPeriod() != null) {
                    System.out.println("Lockout Period: " + renewalTerm.lockoutPeriod());
                }

                if (renewalTerm.maxRenewals() != null) {
                    System.out.println("Max Renewals: " + renewalTerm.maxRenewals());
                }

                if (renewalTerm.adjustmentDeadline() != null) {
                    System.out.println("Adjustment Deadline: " + renewalTerm.adjustmentDeadline());
                }

                printPriceIncrease(renewalTerm.priceIncrease());

                for (TermTemplate termTemplate : renewalTerm.termTemplates()) {
                    printTermTemplate(termTemplate);
                }
            }

            nextToken = response.nextToken();
        } while (nextToken != null);
    }

    /**
     * Prints the price increase that is applied each time the agreement renews.
     */
    private static void printPriceIncrease(PriceIncrease priceIncrease) {
        if (priceIncrease == null) {
            System.out.println("Price Increase: none (no uplift is set, so the agreement renews at "
                                       + "the same price)");
            return;
        }

        if (priceIncrease.fixedPercentage() != null) {
            String fixedPercentage = priceIncrease.fixedPercentage().value();
            if (Double.parseDouble(fixedPercentage) == 0) {
                System.out.println("Fixed Price Increase Percentage: " + fixedPercentage
                                           + " (the agreement renews at the same price)");
            } else {
                System.out.println("Fixed Price Increase Percentage: " + fixedPercentage);
            }
        } else if (priceIncrease.percentageRange() != null) {
            System.out.println("Price Increase Min Percentage: "
                                       + priceIncrease.percentageRange().minValue());
            System.out.println("Price Increase Max Percentage: "
                                       + priceIncrease.percentageRange().maxValue());
            System.out.println("Price Increase Default Percentage: "
                                       + priceIncrease.percentageRange().defaultValue());
        }
    }

    /**
     * TermTemplate is a union. Payment schedules are the only variant the renewal term supports
     * today, so any other variant is skipped rather than printed.
     */
    private static void printTermTemplate(TermTemplate termTemplate) {
        if (termTemplate.paymentScheduleTermTemplate() == null) {
            return;
        }

        System.out.println("Payment Schedule Template:");
        for (PaymentScheduleEntry entry : termTemplate.paymentScheduleTermTemplate().schedule()) {
            String line = "  Charge Date Offset: " + entry.chargeDateOffset()
                                  + ", Charge Percentage: " + entry.chargePercentage();

            if (entry.dayOfMonth() != null) {
                line += ", Day Of Month: " + entry.dayOfMonth();
            }

            System.out.println(line);
        }
    }

    /**
     * Prints the end time behavior of an agreement.
     */
    public static void printEndTimeBehavior(MarketplaceAgreementClient client,
                                            String agreementId,
                                            String label) {
        DescribeAgreementResponse describeAgreementResponse = client.describeAgreement(
                DescribeAgreementRequest.builder().agreementId(agreementId).build());

        EndTimeBehavior endTimeBehavior = describeAgreementResponse.endTimeBehavior();
        if (endTimeBehavior == null) {
            System.out.println(label + " - End Time Behavior: none (this agreement has no end date)");
            return;
        }

        System.out.println(label + " - End Time Behavior Type: " + endTimeBehavior.typeAsString());

        if (endTimeBehavior.reasonCodeAsString() != null) {
            System.out.println(label + " - End Time Behavior Reason Code: "
                                       + endTimeBehavior.reasonCodeAsString());
        }

        if (endTimeBehavior.renewalSummary() != null
                && endTimeBehavior.renewalSummary().offerId() != null) {
            System.out.println(label + " - Renewal Offer ID: "
                                       + endTimeBehavior.renewalSummary().offerId());
        }
    }
}
