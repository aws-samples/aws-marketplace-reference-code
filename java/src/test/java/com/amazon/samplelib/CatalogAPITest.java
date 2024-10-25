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

import com.example.awsmarketplace.catalogapi.DescribeChangeSet;
import com.example.awsmarketplace.catalogapi.DescribeEntity;
import com.example.awsmarketplace.catalogapi.ListAllCppoOffers;
import com.example.awsmarketplace.catalogapi.ListAllPrivateOffers;
import com.example.awsmarketplace.catalogapi.ListAllSharedResaleAuthorizations;
import com.example.awsmarketplace.catalogapi.ListEntities;
import com.example.awsmarketplace.catalogapi.ListProductPrivateOffers;
import com.example.awsmarketplace.catalogapi.ListProductPublicOrPrivateReleasedOffers;

import software.amazon.awssdk.services.marketplacecatalog.model.DescribeChangeSetResponse;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityResponse;
import software.amazon.awssdk.services.marketplacecatalog.model.EntitySummary;
import software.amazon.awssdk.services.marketplacecatalog.model.ListEntitiesResponse;

public class CatalogAPITest {
	@Test
    public void testDescribeChangeset() {
		String changesetId = Helpers.getParameterValue("/capi/changeset-id");
		DescribeChangeSetResponse describeChangeSetResponse = DescribeChangeSet.getDescribeChangeSetResponse(changesetId);
        assertEquals(describeChangeSetResponse.sdkHttpResponse().statusCode(), 200);
	}
	
	@Test
    public void testDescribeEntity() {
		String offerId = Helpers.getParameterValue("/capi/offer-id");
		DescribeEntityResponse describeEntityResponse = DescribeEntity.getDescribeEntityResponse(offerId);
        assertEquals(describeEntityResponse.sdkHttpResponse().statusCode(), 200);
	}
	
	@Test
	public void testListAllCppoOffers() {
		List<String> cppoOfferIds = ListAllCppoOffers.getAllCppoOfferIds();
		assertNotNull(cppoOfferIds);
        assertTrue(cppoOfferIds instanceof List);
        assertFalse(cppoOfferIds.isEmpty());
	}
	
	@Test
	public void testListAllPrivateOffers() {
		String offerReleaseDateAfterValue = "2023-01-01T23:59:59Z";
		String offerAvailableEndDateAfterValue = "2040-12-24T23:59:59Z";
		List<EntitySummary> entitySummaryList = ListAllPrivateOffers.getEntitySummaryList(offerReleaseDateAfterValue, offerAvailableEndDateAfterValue);
		assertNotNull(entitySummaryList);
        assertTrue(entitySummaryList instanceof List);
        assertFalse(entitySummaryList.isEmpty());
	}
	
	@Test
	public void testListAllSharedResaleAuthorizations() {
		List<ListEntitiesResponse> responseList = ListAllSharedResaleAuthorizations.getListEntityResponseList();
		assertNotNull(responseList);
        assertTrue(responseList instanceof List);
        assertFalse(responseList.isEmpty());
	}
	
	@Test
	public void testListEntities() {
		Map<String, List<EntitySummary>> allProductsWithOffers  = ListEntities.getAllProductsWithOffers();
		assertNotNull(allProductsWithOffers);
        assertTrue(allProductsWithOffers instanceof Map);
        if (! allProductsWithOffers.isEmpty()) {
        	for (Map.Entry<String, List<EntitySummary>> productWithOffer : allProductsWithOffers.entrySet()) {
                assertNotNull("Map keys should not be null.", productWithOffer.getKey());
                assertTrue("Map values should be a list of Dimension.", productWithOffer.getValue() instanceof List);
            }
        }
	}
	
	@Test
	public void testListProductPrivateOffers() {
		List<EntitySummary> entitySummaryList = ListProductPrivateOffers.getEntitySummaryList();
		assertNotNull(entitySummaryList);
        assertTrue(entitySummaryList instanceof List);
        assertFalse(entitySummaryList.isEmpty());
	}
	
	@Test
	public void testListProductPublicOrPrivateReleasedOffers() {
		List<EntitySummary> entitySummaryList = ListProductPublicOrPrivateReleasedOffers.getEntitySummaryLIst();
		assertNotNull(entitySummaryList);
        assertTrue(entitySummaryList instanceof List);
        assertFalse(entitySummaryList.isEmpty());
	}
}