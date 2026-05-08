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
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementEntitlementsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementEntitlementsResponse;

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
}
