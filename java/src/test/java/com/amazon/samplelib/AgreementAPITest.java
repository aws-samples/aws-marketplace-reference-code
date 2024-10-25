// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.amazon.samplelib;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

import java.util.List;
import java.util.Map;

import org.junit.Test;

import com.example.awsmarketplace.agreementapi.DescribeAgreement;
import com.example.awsmarketplace.agreementapi.GetAgreementAutoRenewal;
import com.example.awsmarketplace.agreementapi.GetAgreementCustomerInfo;
import com.example.awsmarketplace.agreementapi.GetAgreementFinancialDetails;
import com.example.awsmarketplace.agreementapi.GetAgreementProductType;
import com.example.awsmarketplace.agreementapi.GetAgreementStatus;
import com.example.awsmarketplace.agreementapi.GetAgreementTerms;
import com.example.awsmarketplace.agreementapi.GetAgreementTermsDimensionInstances;
import com.example.awsmarketplace.agreementapi.GetAgreementTermsDimensionPurchased;
import com.example.awsmarketplace.agreementapi.GetAgreementTermsEula;
import com.example.awsmarketplace.agreementapi.GetAgreementTermsFreeTrialDetails;
import com.example.awsmarketplace.agreementapi.GetAgreementTermsPaymentSchedule;
import com.example.awsmarketplace.agreementapi.GetAgreementTermsPricingEachDimension;
import com.example.awsmarketplace.agreementapi.GetAgreementTermsSupportTerm;
import com.example.awsmarketplace.agreementapi.GetAllAgreements;
import com.example.awsmarketplace.agreementapi.GetAllAgreementsIds;
import com.example.awsmarketplace.agreementapi.GetProductAndOfferDetailFromAgreement;
import com.example.awsmarketplace.agreementapi.SearchAgreementsByEndDate;
import com.example.awsmarketplace.agreementapi.SearchAgreementsByOneFilter;
import com.example.awsmarketplace.agreementapi.SearchAgreementsByTwoFilters;

import software.amazon.awssdk.services.marketplaceagreement.model.AgreementViewSummary;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.Dimension;
import software.amazon.awssdk.services.marketplaceagreement.model.DocumentItem;
import software.amazon.awssdk.services.marketplaceagreement.model.FreeTrialPricingTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.SupportTerm;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityResponse;

public class AgreementAPITest {
	@Test
    public void testDescribeAgreement() {
		String agreementId = Helpers.getParameterValue("/ag/describe/agreement-id");
        DescribeAgreementResponse response = DescribeAgreement.getResponse(agreementId);
        assertEquals(response.sdkHttpResponse().statusCode(), 200);
	}
	
	@Test
	public void testGetAllAgreements() {
		List<AgreementViewSummary> agreementSummaryList = GetAllAgreements.getAllAgreements();
        assertNotNull(agreementSummaryList);
        assertTrue(agreementSummaryList instanceof List);
        assertFalse(agreementSummaryList.isEmpty());
	}
	
	@Test
	public void testSearchAgreementsByOneFilter() {
		List<AgreementViewSummary> agreementSummaryList = SearchAgreementsByOneFilter.getAgreements();
        assertNotNull(agreementSummaryList);
        assertTrue(agreementSummaryList instanceof List);
        assertFalse(agreementSummaryList.isEmpty());
	}
	
	@Test
	public void testSearchAgreementsByTwoFilters() {
		List<AgreementViewSummary> agreementSummaryList = SearchAgreementsByTwoFilters.getAgreements();
        assertNotNull(agreementSummaryList);
        assertTrue(agreementSummaryList instanceof List);
        assertFalse(agreementSummaryList.isEmpty());
	}
	
	@Test
	public void testSearchAgreementsByEndDate() {
		List<AgreementViewSummary> agreementSummaryList = SearchAgreementsByEndDate.getAgreements();
        assertNotNull(agreementSummaryList);
        assertTrue(agreementSummaryList instanceof List);
        assertFalse(agreementSummaryList.isEmpty());
	}

	@Test
	public void testGetProductAndOfferDetailFromAgreement() {
		String agreementId = Helpers.getParameterValue("/ag//getProductOfferDetail/agreement-id");
		List<DescribeEntityResponse> entityResponseList = GetProductAndOfferDetailFromAgreement.getEntities(agreementId);
        assertNotNull(entityResponseList);
        assertTrue(entityResponseList instanceof List);
        assertFalse(entityResponseList.isEmpty());
	}
	
	@Test
	public void testGetAllAgreementIds() {
		List<String> agreementIds = GetAllAgreementsIds.getAllAgreementIds();
        assertNotNull(agreementIds);
        assertTrue(agreementIds instanceof List);
        assertFalse(agreementIds.isEmpty());
	}
	
	@Test
	public void testGetAgreementTermsSupportTerms() {
		String agreementId = Helpers.getParameterValue("/ag/supportTerms/agreement-id");
		List<SupportTerm> supportTerms = GetAgreementTermsSupportTerm.getSupportTerms(agreementId);
		assertNotNull(supportTerms);
        assertTrue(supportTerms instanceof List);
        assertFalse(supportTerms.isEmpty());
	}
	
	@Test
	public void testGetAgreementTermsPricingEachDimension() {
		String agreementId = Helpers.getParameterValue("/ag/pricingForEachDimension/agreement-id");
		List<Object> dimensions = GetAgreementTermsPricingEachDimension.getDimensions(agreementId);
		assertNotNull(dimensions);
        assertTrue(dimensions instanceof List);
        assertFalse(dimensions.isEmpty());
	}
	
	@Test
	public void testGetAgreementTermsPaymentSchedule() {
		String agreementId = Helpers.getParameterValue("/ag/paymentSchedule/agreement-id");
		List<Map<String, Object>> paymentScheduleArray = GetAgreementTermsPaymentSchedule.getPaymentSchedules(agreementId);
		assertNotNull(paymentScheduleArray);
        assertTrue(paymentScheduleArray instanceof List);
        assertFalse(paymentScheduleArray.isEmpty());
	}
	
	@Test
	public void testGetAgreementTermsFreeTrialDetails() {
		String agreementId = Helpers.getParameterValue("/ag/freeTrial/agreement-id");
		List<FreeTrialPricingTerm> freeTrialPricingTerms = GetAgreementTermsFreeTrialDetails.getFreeTrialPricingTerms(agreementId);
		assertNotNull(freeTrialPricingTerms);
        assertTrue(freeTrialPricingTerms instanceof List);
        assertFalse(freeTrialPricingTerms.isEmpty());
	}
	
	@Test
	public void testGetAgreementTermsEula() {
		String agreementId = Helpers.getParameterValue("/ag/eula/agreement-id");
		List<DocumentItem> legalEulaArray = GetAgreementTermsEula.getLegalEula(agreementId);
		assertNotNull(legalEulaArray);
        assertTrue(legalEulaArray instanceof List);
        assertFalse(legalEulaArray.isEmpty());
	}
	
	@Test
	public void testGetAgreementTermsDimensionPurchased() {
		String agreementId = Helpers.getParameterValue("/ag/dimensionPurchased/agreement-id");
		List<String> dimensionKeys = GetAgreementTermsDimensionPurchased.getDimensionKeys(agreementId);
		assertNotNull(dimensionKeys);
        assertTrue(dimensionKeys instanceof List);
        assertFalse(dimensionKeys.isEmpty());
	}
	
	@Test
	public void testGetAgreementTermsDimensionInstances() {
		String agreementId = Helpers.getParameterValue("/ag/dimensionInstances/agreement-id");
		Map<String, List<Dimension>> dimensionMap =GetAgreementTermsDimensionInstances.getDimensions(agreementId);
		assertNotNull(dimensionMap);
        assertTrue(dimensionMap instanceof Map);
        if (! dimensionMap.isEmpty()) {
        	for (Map.Entry<String, List<Dimension>> dimension : dimensionMap.entrySet()) {
                assertNotNull("Map keys should not be null.", dimension.getKey());
                assertTrue("Map values should be a list of Dimension.", dimension.getValue() instanceof List);
            }
        }
	}
	
	@Test
    public void testGetAgreementTerms() {
		String agreementId = Helpers.getParameterValue("/ag/terms/agreement-id");
		GetAgreementTermsResponse getAgreementTermsResponse = GetAgreementTerms.getAgreementTermsResponse(agreementId);
        assertEquals(getAgreementTermsResponse.sdkHttpResponse().statusCode(), 200);
	}
	
	@Test
    public void testGetAgreementStatus() {
		String agreementId = Helpers.getParameterValue("/ag/status/agreement-id");
		DescribeAgreementResponse describeAgreementResponse = GetAgreementStatus.getDescribeAgreementResponse(agreementId);
        assertEquals(describeAgreementResponse.sdkHttpResponse().statusCode(), 200);
	}
	
	@Test
	public void testGetAgreementProductType() {
		String agreementId = Helpers.getParameterValue("/ag/productType/agreement-id");
		List<String> productIds = GetAgreementProductType.getProducts(agreementId);
		assertNotNull(productIds);
        assertTrue(productIds instanceof List);
        assertFalse(productIds.isEmpty());
	}
	
	@Test
	public void testGetAgreementFinancialDetails() {
		String agreementId = Helpers.getParameterValue("/ag/financialDetails/agreement-id");
		String totalContractValue = GetAgreementFinancialDetails.getTotalContractValue(agreementId);
		assertNotNull(totalContractValue);
	}
	
	@Test
    public void testGetAgreementCustomerInfo() {
		String agreementId = Helpers.getParameterValue("/ag/customerInfo/agreement-id");
		DescribeAgreementResponse describeAgreementResponse = GetAgreementCustomerInfo.getDescribeAgreementResponse(agreementId);
        assertEquals(describeAgreementResponse.sdkHttpResponse().statusCode(), 200);
	}
	
	@Test
	public void testGetAgreementAutoRenewal() {
		String agreementId = Helpers.getParameterValue("/ag/autoRenewal/agreement-id");
		String autoRenewal = GetAgreementAutoRenewal.getAutoRenewal(agreementId);
		assertNotNull(autoRenewal);
	}
	
}