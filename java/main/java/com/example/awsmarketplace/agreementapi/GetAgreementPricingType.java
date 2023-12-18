package com.example.awsmarketplace.agreementapi;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.AgreementViewSummary;
import software.amazon.awssdk.services.marketplaceagreement.model.Filter;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.GetAgreementTermsResponse;
import software.amazon.awssdk.services.marketplaceagreement.model.SearchAgreementsRequest;
import software.amazon.awssdk.services.marketplaceagreement.model.SearchAgreementsResponse;

import com.fasterxml.jackson.annotation.JsonAutoDetect.Visibility;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

import org.apache.commons.lang3.tuple.Triple;

import software.amazon.awssdk.services.marketplacecatalog.MarketplaceCatalogClient;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.DescribeEntityResponse;

import static com.example.awsmarketplace.utils.ReferenceCodesConstants.*;
import com.fasterxml.jackson.annotation.PropertyAccessor;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

/*
 * Obtain the pricing type of the agreement (contract, FPS, metered, free etc.)
 */
public class GetAgreementPricingType {

	private static final String FILTER_NAME = "OfferId";

	private static final String FILTER_VALUE = OFFER_ID;
	
	// Product types
	private static final String SAAS_PRODUCT = "SaaSProduct";
	private static final String AMI_PRODUCT = "AmiProduct";
	private static final String ML_PRODUCT = "MachineLearningProduct";
	private static final String CONTAINER_PRODUCT = "ContainerProduct";
	private static final String DATA_PRODUCT = "DataProduct";
	private static final String PROSERVICE_PRODUCT = "ProfessionalServicesProduct";
	private static final String AIQ_PRODUCT = "AiqProduct";

	// Pricing types
	private static final String CCP = "CCP";
	private static final String ANNUAL = "Annual";
	private static final String CONTRACT = "Contract";
	private static final String SFT = "SaaS Free Trial";
	private static final String HMA = "Hourly and Monthly Agreements";
	private static final String HOURLY = "Hourly";
	private static final String MONTHLY = "Monthly";
	private static final String AFPS = "Annual FPS";
	private static final String CFPS = "Contract FPS";
	private static final String CCPFPS = "CCP with FPS";
	private static final String BYOL = "BYOL";
	private static final String FREE = "Free";
	private static final String FTH = "Free Trials and Hourly";

	// Agreement term pricing types
	private static final Set<String> LEGAL = Set.of("LegalTerm");
	private static final Set<String> CONFIGURABLE_UPFRONT = Set.of("ConfigurableUpfrontPricingTerm");
	private static final Set<String> USAGE_BASED = Set.of("UsageBasedPricingTerm");
	private static final Set<String> CONFIGURABLE_UPFRONT_AND_USAGE_BASED = Set.of("ConfigurableUpfrontPricingTerm", "UsageBasedPricingTerm");
	private static final Set<String> FREE_TRIAL = Set.of("FreeTrialPricingTerm");
	private static final Set<String> RECURRING_PAYMENT = Set.of("RecurringPaymentTerm");
	private static final Set<String> USAGE_BASED_AND_RECURRING_PAYMENT = Set.of("UsageBasedPricingTerm", "RecurringPaymentTerm");
	private static final Set<String> FIXED_UPFRONT_AND_PAYMENT_SCHEDULE = Set.of("FixedUpfrontPricingTerm", "PaymentScheduleTerm");
	private static final Set<String> FIXED_UPFRONT_AND_PAYMENT_SCHEDULE_AND_USAGE_BASED = Set.of("FixedUpfrontPricingTerm", "PaymentScheduleTerm", "UsageBasedPricingTerm");
	private static final Set<String> BYOL_PRICING = Set.of("ByolPricingTerm");
	private static final Set<String> FREE_TRIAL_AND_USAGE_BASED = Set.of("FreeTrialPricingTerm", "UsageBasedPricingTerm");

	private static final List<Set<String>> ALL_AGREEMENT_TERM_TYPES_COMBINATION = Arrays.asList(LEGAL, CONFIGURABLE_UPFRONT, USAGE_BASED, CONFIGURABLE_UPFRONT_AND_USAGE_BASED,
			FREE_TRIAL, RECURRING_PAYMENT, USAGE_BASED_AND_RECURRING_PAYMENT, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE_AND_USAGE_BASED, BYOL_PRICING, FREE_TRIAL_AND_USAGE_BASED);
	
	private static  MarketplaceAgreementClient marketplaceAgreementClient = 
			MarketplaceAgreementClient.builder()
			.httpClient(ApacheHttpClient.builder().build())
			.credentialsProvider(ProfileCredentialsProvider.create())
			.build();

	private static MarketplaceCatalogClient marketplaceCatalogClient = 
			MarketplaceCatalogClient.builder()
			.httpClient(ApacheHttpClient.builder().build())
			.credentialsProvider(ProfileCredentialsProvider.create())
			.build();

    /*
     * Get agreement Pricing Type given product type, agreement term types and offer types if needed
     */
	public static String getPricingType(String productType, Set<String> agreementTermType, Set<String> offerType) {
		Map<Triple<String, Set<String>, Set<String>>, String> pricingTypes = new HashMap<>();

		pricingTypes.put(Triple.of(SAAS_PRODUCT, CONFIGURABLE_UPFRONT_AND_USAGE_BASED, new HashSet<>()), CCP);
		pricingTypes.put(Triple.of(DATA_PRODUCT, CONFIGURABLE_UPFRONT_AND_USAGE_BASED, new HashSet<>()), CCP);
		pricingTypes.put(Triple.of(CONTAINER_PRODUCT, CONFIGURABLE_UPFRONT, CONFIGURABLE_UPFRONT_AND_USAGE_BASED), ANNUAL);
		pricingTypes.put(Triple.of(AMI_PRODUCT, CONFIGURABLE_UPFRONT, CONFIGURABLE_UPFRONT_AND_USAGE_BASED), ANNUAL);
		pricingTypes.put(Triple.of(ML_PRODUCT, CONFIGURABLE_UPFRONT, CONFIGURABLE_UPFRONT_AND_USAGE_BASED), ANNUAL);
		pricingTypes.put(Triple.of(CONTAINER_PRODUCT, CONFIGURABLE_UPFRONT, CONFIGURABLE_UPFRONT), CONTRACT);
		pricingTypes.put(Triple.of(AMI_PRODUCT, CONFIGURABLE_UPFRONT, CONFIGURABLE_UPFRONT), CONTRACT);
		pricingTypes.put(Triple.of(SAAS_PRODUCT, CONFIGURABLE_UPFRONT, new HashSet<>()), CONTRACT);
		pricingTypes.put(Triple.of(DATA_PRODUCT, CONFIGURABLE_UPFRONT, new HashSet<>()), CONTRACT);
		pricingTypes.put(Triple.of(AIQ_PRODUCT, CONFIGURABLE_UPFRONT, new HashSet<>()), CONTRACT);
		pricingTypes.put(Triple.of(PROSERVICE_PRODUCT, CONFIGURABLE_UPFRONT, new HashSet<>()), CONTRACT);
		pricingTypes.put(Triple.of(SAAS_PRODUCT, FREE_TRIAL, new HashSet<>()), SFT);
		pricingTypes.put(Triple.of(AMI_PRODUCT, USAGE_BASED_AND_RECURRING_PAYMENT, new HashSet<>()), HMA);
		pricingTypes.put(Triple.of(SAAS_PRODUCT, USAGE_BASED, new HashSet<>()), HOURLY);
		pricingTypes.put(Triple.of(AMI_PRODUCT, USAGE_BASED, new HashSet<>()), HOURLY);
		pricingTypes.put(Triple.of(ML_PRODUCT, USAGE_BASED, new HashSet<>()), HOURLY);
		pricingTypes.put(Triple.of(CONTAINER_PRODUCT, RECURRING_PAYMENT, new HashSet<>()), MONTHLY);
		pricingTypes.put(Triple.of(AMI_PRODUCT, RECURRING_PAYMENT, new HashSet<>()), MONTHLY);
		pricingTypes.put(Triple.of(CONTAINER_PRODUCT, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE_AND_USAGE_BASED), AFPS);
		pricingTypes.put(Triple.of(AMI_PRODUCT, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE_AND_USAGE_BASED), AFPS);
		pricingTypes.put(Triple.of(ML_PRODUCT, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE, new HashSet<>()), AFPS);
		pricingTypes.put(Triple.of(CONTAINER_PRODUCT, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE, new HashSet<>()), CFPS);
		pricingTypes.put(Triple.of(AMI_PRODUCT, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE), CFPS);
		pricingTypes.put(Triple.of(SAAS_PRODUCT, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE, new HashSet<>()), CFPS);
		pricingTypes.put(Triple.of(DATA_PRODUCT, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE, new HashSet<>()), CFPS);
		pricingTypes.put(Triple.of(AIQ_PRODUCT, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE, new HashSet<>()), CFPS);
		pricingTypes.put(Triple.of(PROSERVICE_PRODUCT, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE, new HashSet<>()), CFPS);
		pricingTypes.put(Triple.of(SAAS_PRODUCT, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE_AND_USAGE_BASED, new HashSet<>()), CCPFPS);
		pricingTypes.put(Triple.of(DATA_PRODUCT, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE_AND_USAGE_BASED, new HashSet<>()), CCPFPS);
		pricingTypes.put(Triple.of(AIQ_PRODUCT, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE_AND_USAGE_BASED, new HashSet<>()), CCPFPS);
		pricingTypes.put(Triple.of(PROSERVICE_PRODUCT, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE_AND_USAGE_BASED, new HashSet<>()), CCPFPS);
		pricingTypes.put(Triple.of(AMI_PRODUCT, BYOL_PRICING, new HashSet<>()), BYOL);
		pricingTypes.put(Triple.of(SAAS_PRODUCT, BYOL_PRICING, new HashSet<>()), BYOL);
		pricingTypes.put(Triple.of(PROSERVICE_PRODUCT, BYOL_PRICING, new HashSet<>()), BYOL);
		pricingTypes.put(Triple.of(AIQ_PRODUCT, BYOL_PRICING, new HashSet<>()), BYOL);
		pricingTypes.put(Triple.of(ML_PRODUCT, BYOL_PRICING, new HashSet<>()), BYOL);
		pricingTypes.put(Triple.of(CONTAINER_PRODUCT, BYOL_PRICING, new HashSet<>()), BYOL);
		pricingTypes.put(Triple.of(DATA_PRODUCT, BYOL_PRICING, new HashSet<>()), BYOL);
		pricingTypes.put(Triple.of(CONTAINER_PRODUCT, LEGAL, new HashSet<>()), FREE);
		pricingTypes.put(Triple.of(AMI_PRODUCT, FREE_TRIAL_AND_USAGE_BASED, new HashSet<>()), FTH);
		pricingTypes.put(Triple.of(CONTAINER_PRODUCT, FREE_TRIAL_AND_USAGE_BASED, new HashSet<>()), FTH);
		pricingTypes.put(Triple.of(ML_PRODUCT, FREE_TRIAL_AND_USAGE_BASED, new HashSet<>()), FTH);

		Triple<String, Set<String>, Set<String>> key = Triple.of(productType, agreementTermType, offerType);

		if (pricingTypes.containsKey(key)) {
			return pricingTypes.get(key);
		} else {
			return "Unknown";
		}
	}

	/*
	 * Given product type and agreement term types, some combinations need to check offer term types as well.
	 */
	public static String needToCheckOfferTermsType(String productType, Set<String> agreementTermTypes) {
		Map<KeyPair, String> offerTermTypes = new HashMap<>();
		offerTermTypes.put(new KeyPair(CONTAINER_PRODUCT, CONFIGURABLE_UPFRONT), "Y");
		offerTermTypes.put(new KeyPair(AMI_PRODUCT, CONFIGURABLE_UPFRONT), "Y");
		offerTermTypes.put(new KeyPair(CONTAINER_PRODUCT, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE), "Y");
		offerTermTypes.put(new KeyPair(AMI_PRODUCT, FIXED_UPFRONT_AND_PAYMENT_SCHEDULE), "Y");

		KeyPair key = new KeyPair(productType, agreementTermTypes);
		if (offerTermTypes.containsKey(key)) {
			return offerTermTypes.get(key);
		} else {
			return null;
		}
	}

	public static List<AgreementViewSummary> getAgreementsById() {
		
		List<AgreementViewSummary> agreementSummaryList = new ArrayList<AgreementViewSummary>();

		Filter partyType = Filter.builder().name(PARTY_TYPE_FILTER_NAME).values(PARTY_TYPE_FILTER_VALUE_PROPOSER).build();

		Filter agreementType = Filter.builder().name(AGREEMENT_TYPE_FILTER_NAME).values(AGREEMENT_TYPE_FILTER_VALUE_PURCHASEAGREEMENT).build();

		Filter customizeFilter = Filter.builder().name(FILTER_NAME).values(FILTER_VALUE).build();

		SearchAgreementsRequest searchAgreementsRequest = 
				SearchAgreementsRequest.builder()
				.catalog(AWS_MP_CATALOG)
				.filters(partyType, agreementType, customizeFilter).build();

		SearchAgreementsResponse searchResultResponse = marketplaceAgreementClient.searchAgreements(searchAgreementsRequest);

		agreementSummaryList.addAll(searchResultResponse.agreementViewSummaries());

		while (searchResultResponse.nextToken() != null && searchResultResponse.nextToken().length() > 0) {
			searchAgreementsRequest = SearchAgreementsRequest.builder().catalog(AWS_MP_CATALOG)
					.filters(partyType, agreementType).nextToken(searchResultResponse.nextToken()).build();
			searchResultResponse = marketplaceAgreementClient.searchAgreements(searchAgreementsRequest);
			agreementSummaryList.addAll(searchResultResponse.agreementViewSummaries());
		}
		return agreementSummaryList;

	}

	static class KeyPair {
		private final String first;
		private final Set<String> second;

		public KeyPair(String productType, Set<String> second) {
			this.first = productType;
			this.second = second;
		}

		@Override
		public int hashCode() {
			return Objects.hash(first, second);
		}

		@Override
		public boolean equals(Object obj) {
			if (this == obj)
				return true;
			if (obj == null || getClass() != obj.getClass())
				return false;
			KeyPair other = (KeyPair) obj;
			return Objects.equals(first, other.first) && Objects.equals(second, other.second);
		}
	}

	/*
	 * Get all the term types for the offer
	 */
	public static Set<String> getOfferTermTypes(String offerId) {

		Set<String> offerTermTypes = new HashSet<String>();

		DescribeEntityRequest request = 
				DescribeEntityRequest.builder()
				.catalog(AWS_MP_CATALOG)
				.entityId(offerId)
				.build();

		DescribeEntityResponse result = marketplaceCatalogClient.describeEntity(request);

		String details = result.details();
		
		try {
			ObjectMapper objectMapper = new ObjectMapper();
			JsonNode rootNode = objectMapper.readTree(details);
			JsonNode termsNode = rootNode.get(ATTRIBUTE_TERMS);

			for (JsonNode termNode : termsNode) {
				if (termNode.get(ATTRIBUTE_TYPE_ENTITY) != null ) {
					offerTermTypes.add(termNode.get(ATTRIBUTE_TYPE_ENTITY).asText());
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
		}

		return offerTermTypes;

	}

	/*
	 * Get all the agreement term types
	 */
	public static Set<String> getAgreementTermTypes(GetAgreementTermsResponse agreementTerm) {
		Set<String> agreementTermTypes = new HashSet<String>();
		try {
			for (AcceptedTerm term : agreementTerm.acceptedTerms()) {
				ObjectMapper objectMapper = new ObjectMapper();
				JsonNode termNode = objectMapper.readTree(getJson(term));
				Iterator<Map.Entry<String, JsonNode>> fieldsIterator = termNode.fields();
				while (fieldsIterator.hasNext()) {
					Map.Entry<String, JsonNode> entry = fieldsIterator.next();
					JsonNode value = entry.getValue();
					if (value.isObject() && value.has(ATTRIBUTE_TYPE_AGREEMENT)) {
						agreementTermTypes.add(value.get(ATTRIBUTE_TYPE_AGREEMENT).asText());
					}
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
		return agreementTermTypes;

	}

	/*
	 * make sure all elements in array2 exist in array1
	 */
	public static boolean allElementsExist(Set<String> array1, Set<String> array2) {
		for (String element : array2) {
			boolean found = false;
			for (String str : array1) {
				if (element.equals(str)) {
					found = true;
					break;
				}
			}
			if (!found) {
				return false;
			}
		}
		return true;
	}

	/*
	 * Find the combinations of the agreement term types for the agreement
	 */
	public static Set<String> getMatchedTermTypesCombination(Set<String> agreementTermTypes) {
		Set<String> matchedCombination = new HashSet<String>();
		for (Set<String> element : ALL_AGREEMENT_TERM_TYPES_COMBINATION) {
			if (allElementsExist(agreementTermTypes, element)) {
				matchedCombination = element;
			}
		}
		return matchedCombination;
	}

	public static void main(String[] args) {

		List<AgreementViewSummary> agreements = getAgreementsById();

		for (AgreementViewSummary summary : agreements) {
			String pricingType = "";
			String agreementId = summary.agreementId();
			System.out.println(agreementId);
			String offerId = summary.proposalSummary().offerId();
			
			//get all pricing term types for the offer in the agreement
			Set<String> offerTermTypes = getOfferTermTypes(offerId);
			String productType = summary.proposalSummary().resources().get(0).type();
			
			//get all pricing term types for the agreement
			GetAgreementTermsRequest getAgreementTermsRequest = 
					GetAgreementTermsRequest.builder().agreementId(agreementId)
					.build();
			GetAgreementTermsResponse getAgreementTermsResponse = marketplaceAgreementClient.getAgreementTerms(getAgreementTermsRequest);
			Set<String> agreementTermTypes = getAgreementTermTypes(getAgreementTermsResponse);
			
			//get matched pricing term type combination set
			Set<String> agreementMatchedTermType = getMatchedTermTypesCombination(agreementTermTypes);
			
			//check to see if this agreement pricing term combination needs additional check on offer pricing terms
			String needToCheckOfferType = needToCheckOfferTermsType(productType, agreementMatchedTermType);
			
			// get the pricing type for the agreement based on the product type, agreement term types and offer term types if needed
			if (needToCheckOfferType != null) {
				Set<String> offerMatchedTermType = getMatchedTermTypesCombination(offerTermTypes);
				pricingType = getPricingType(productType, agreementMatchedTermType, offerMatchedTermType);
			} else if (agreementMatchedTermType == LEGAL) {
				pricingType = FREE;
			} else {
				pricingType = getPricingType(productType, agreementMatchedTermType, new HashSet());
			}
			System.out.println("Pricing type is " + pricingType);
		}
	}

	private static String getJson(Object result) {
		String json = "";

		try {
			ObjectMapper om = new ObjectMapper();
			om.setVisibility(PropertyAccessor.FIELD, Visibility.ANY);
			om.registerModule(new JavaTimeModule());
			ObjectWriter ow = om.writer().withDefaultPrettyPrinter();

			json = ow.writeValueAsString(result);
		} catch (JsonProcessingException e) {
			e.printStackTrace();
		}
		return json;
	}

}
