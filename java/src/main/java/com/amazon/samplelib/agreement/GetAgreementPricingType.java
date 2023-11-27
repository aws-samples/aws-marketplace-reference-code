//AG-18 Obtain the EULA I have entered into with my customer via the agreement
package com.amazon.samplelib.agreement;

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

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;
import com.fasterxml.jackson.annotation.PropertyAccessor;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

public class GetAgreementPricingType {
	
	private static final String idType = "OfferId";
	
	private static final String idValue = ReferenceCodesConstants.OFFER_ID;
	
	private static MarketplaceAgreementClient mpasClient = ReferenceCodesUtils.getMPAgreementClient();

	private static MarketplaceCatalogClient awsMarketplaceCatalog = ReferenceCodesUtils.getMPCatalogClient();

	  // Product types
    private static final String SaaSProduct = "SaaSProduct";
    private static final String AmiProduct = "AmiProduct";
    private static final String MLProduct = "MachineLearningProduct";
    private static final String ContainerProduct = "ContainerProduct";
    private static final String DataProduct = "DataProduct";
    private static final String ProServiceProduct = "ProfessionalServicesProduct";
    private static final String AiqProduct = "AiqProduct";

    // Pricing types
    private static final String CCP = "CCP";
    private static final String Annual = "Annual";
    private static final String Contract = "Contract";
    private static final String SFT = "SaaS Free Trial";
    private static final String HMA = "Hourly and Monthly Agreements";
    private static final String Hourly = "Hourly";
    private static final String Monthly = "Monthly";
    private static final String AFPS = "Annual FPS";
    private static final String CFPS = "Contract FPS";
    private static final String CCPFPS = "CCP with FPS";
    private static final String BYOL = "BYOL";
    private static final String Free = "Free";
    private static final String FTH = "Free Trials and Hourly";    

    // Agreement term types
    private static final Set<String> legal = Set.of("LegalTerm");
    private static final Set<String> config = Set.of("ConfigurableUpfrontPricingTerm");
    private static final Set<String> usage = Set.of("UsageBasedPricingTerm");
    private static final Set<String> configUsage = Set.of("ConfigurableUpfrontPricingTerm","UsageBasedPricingTerm"); 
    private static final Set<String> freeTrial = Set.of("FreeTrialPricingTerm");
    private static final Set<String> recur = Set.of("RecurringPaymentTerm");
    private static final Set<String> usageRecur = Set.of("UsageBasedPricingTerm","RecurringPaymentTerm");
    private static final Set<String> fixedPayment = Set.of("FixedUpfrontPricingTerm", "PaymentScheduleTerm");
    private static final Set<String> fixedPaymentUsage = Set.of("FixedUpfrontPricingTerm", "PaymentScheduleTerm", "UsageBasedPricingTerm");
    private static final Set<String> byol = Set.of("ByolPricingTerm");
    private static final Set<String> freeTrialUsage = Set.of("FreeTrialPricingTerm", "UsageBasedPricingTerm");

    private static List<Set<String>> allAgreementTypesCombination = Arrays.asList(
    		legal,config, usage, configUsage, freeTrial, recur, usageRecur, fixedPayment, fixedPaymentUsage, byol, freeTrialUsage	
    );
    
    

    public static String getPricingType(String productType, Set<String> agreementTermType, Set<String> offerType) {
        Map<Triple<String, Set<String>, Set<String>>, String> pricingTypes = new HashMap<>();
        
        pricingTypes.put(Triple.of(SaaSProduct, configUsage, new HashSet<>()), CCP);
        pricingTypes.put(Triple.of(DataProduct, configUsage, new HashSet<>()), CCP);
        pricingTypes.put(Triple.of(ContainerProduct, config, configUsage), Annual);
        pricingTypes.put(Triple.of(AmiProduct, config, configUsage), Annual);
        pricingTypes.put(Triple.of(MLProduct, config, configUsage), Annual);
        pricingTypes.put(Triple.of(ContainerProduct, config, config), Contract);
        pricingTypes.put(Triple.of(AmiProduct, config, config), Contract);
        pricingTypes.put(Triple.of(SaaSProduct, config,  new HashSet<>()), Contract);
        pricingTypes.put(Triple.of(DataProduct, config,  new HashSet<>()), Contract);
        pricingTypes.put(Triple.of(AiqProduct, config,  new HashSet<>()), Contract);
        pricingTypes.put(Triple.of(ProServiceProduct, config,  new HashSet<>()), Contract);
        pricingTypes.put(Triple.of(SaaSProduct, freeTrial,  new HashSet<>()), SFT);
        pricingTypes.put(Triple.of(AmiProduct, usageRecur,  new HashSet<>()), HMA);
        pricingTypes.put(Triple.of(SaaSProduct, usage,  new HashSet<>()), Hourly);
        pricingTypes.put(Triple.of(AmiProduct, usage,  new HashSet<>()), Hourly);
        pricingTypes.put(Triple.of(MLProduct, usage,  new HashSet<>()), Hourly);
        pricingTypes.put(Triple.of(ContainerProduct, recur,  new HashSet<>()), Monthly);
        pricingTypes.put(Triple.of(AmiProduct, recur,  new HashSet<>()), Monthly);
        pricingTypes.put(Triple.of(ContainerProduct, fixedPayment,  fixedPaymentUsage), AFPS);
        pricingTypes.put(Triple.of(AmiProduct, fixedPayment, fixedPaymentUsage), AFPS);
        pricingTypes.put(Triple.of(MLProduct, fixedPayment, new HashSet<>()),AFPS);
        pricingTypes.put(Triple.of(ContainerProduct, fixedPayment, new HashSet<>()),CFPS);
        pricingTypes.put(Triple.of(AmiProduct, fixedPayment, fixedPayment),CFPS);
        pricingTypes.put(Triple.of(SaaSProduct, fixedPayment, new HashSet<>()),CFPS);
        pricingTypes.put(Triple.of(DataProduct, fixedPayment, new HashSet<>()),CFPS);
        pricingTypes.put(Triple.of(AiqProduct, fixedPayment, new HashSet<>()),CFPS);
        pricingTypes.put(Triple.of(ProServiceProduct, fixedPayment, new HashSet<>()),CFPS);
        pricingTypes.put(Triple.of(SaaSProduct, fixedPaymentUsage, new HashSet<>()),CCPFPS);
        pricingTypes.put(Triple.of(DataProduct, fixedPaymentUsage, new HashSet<>()),CCPFPS);
        pricingTypes.put(Triple.of(AiqProduct, fixedPaymentUsage, new HashSet<>()),CCPFPS);
        pricingTypes.put(Triple.of(ProServiceProduct, fixedPaymentUsage, new HashSet<>()),CCPFPS);
        pricingTypes.put(Triple.of(AmiProduct, byol, new HashSet<>()),BYOL);
        pricingTypes.put(Triple.of(SaaSProduct, byol, new HashSet<>()),BYOL);
        pricingTypes.put(Triple.of(ProServiceProduct, byol, new HashSet<>()),BYOL);
        pricingTypes.put(Triple.of(AiqProduct, byol, new HashSet<>()),BYOL);
        pricingTypes.put(Triple.of(MLProduct, byol, new HashSet<>()),BYOL);
        pricingTypes.put(Triple.of(ContainerProduct, byol, new HashSet<>()),BYOL);
        pricingTypes.put(Triple.of(DataProduct, byol, new HashSet<>()),BYOL);
        pricingTypes.put(Triple.of(ContainerProduct, legal, new HashSet<>()),Free);
        pricingTypes.put(Triple.of(AmiProduct, freeTrialUsage, new HashSet<>()),FTH);
        pricingTypes.put(Triple.of(ContainerProduct, freeTrialUsage, new HashSet<>()),FTH);
        pricingTypes.put(Triple.of(MLProduct, freeTrialUsage, new HashSet<>()),FTH);

        Triple<String, Set<String>, Set<String>> key = Triple.of(productType, agreementTermType, offerType);
        
        if (pricingTypes.containsKey(key)) {
            return pricingTypes.get(key);
        } else {
            return "Unknown";
        }
    }
    
    public static String needToCheckOfferTermsType(String productType, Set<String>agreementTermTypes) {
    	Map<KeyPair, String> offerTermTypes = new HashMap<>();
    	offerTermTypes.put(new KeyPair(ContainerProduct, config), "Y");
    	offerTermTypes.put(new KeyPair(AmiProduct, config), "Y");
    	offerTermTypes.put(new KeyPair(ContainerProduct, fixedPayment), "Y");
    	offerTermTypes.put(new KeyPair(AmiProduct, fixedPayment), "Y");

    	KeyPair key = new KeyPair(productType, agreementTermTypes);
    	if (offerTermTypes.containsKey(key)) {
            return offerTermTypes.get(key);
        } else {
            return null; // or some other appropriate value
        }
    }
    
    public static List<AgreementViewSummary> getAgreementsById () {
    	List<AgreementViewSummary> agreementSummaryList = new ArrayList<AgreementViewSummary>();
		
		Filter partyType = Filter.builder()
                .name("PartyType")
                .values("Proposer")
                .build();
		
		Filter agreementType = Filter.builder()
                .name("AgreementType")
                .values("PurchaseAgreement")
                .build();
		
		Filter idFilter = Filter.builder()
                .name(idType)
                .values(idValue)
                .build();
		
		SearchAgreementsRequest searchAgreementsRequest = SearchAgreementsRequest.builder()
                .catalog("AWSMarketplace")
                .filters(partyType, agreementType, idFilter)
                .build();
		
		SearchAgreementsResponse searchResult = mpasClient.searchAgreements(searchAgreementsRequest);
		
		agreementSummaryList.addAll(searchResult.agreementViewSummaries());
		
		while (searchResult.nextToken() != null && searchResult.nextToken().length() > 0 ) {
			searchAgreementsRequest = SearchAgreementsRequest.builder()
	                .catalog("AWSMarketplace")
	                .filters(partyType, agreementType)
	                .nextToken(searchResult.nextToken())
	                .build();
			searchResult = mpasClient.searchAgreements(searchAgreementsRequest);
			agreementSummaryList.addAll(searchResult.agreementViewSummaries());
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
            // Implement a suitable hashCode() method
            // Combine hash codes of 'first' and 'second'
            return Objects.hash(first, second);
        }

        @Override
        public boolean equals(Object obj) {
            // Implement a suitable equals() method
            // Compare 'first' and 'second' fields for equality
            if (this == obj) return true;
            if (obj == null || getClass() != obj.getClass()) return false;
            KeyPair other = (KeyPair) obj;
            return Objects.equals(first, other.first) && Objects.equals(second, other.second);
        }
    }
    
    public static Set<String> getOfferTermTypes(String offerId ) {
    	
    	Set<String> offerTermTypes = new HashSet<String>();
		
    	DescribeEntityRequest request = DescribeEntityRequest.builder().catalog("AWSMarketplace").entityId(offerId).build();

		DescribeEntityResponse result = awsMarketplaceCatalog.describeEntity(request);

        String details = result.details();
        
        try {
            ObjectMapper objectMapper = new ObjectMapper();
            JsonNode rootNode = objectMapper.readTree(details);
            JsonNode termsNode = rootNode.get("Terms");

            for (JsonNode termNode : termsNode) {
                String type = termNode.get("Type").asText();
                offerTermTypes.add(type);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        
		return offerTermTypes;
    	
    }

    public static Set<String> getAgreementTermTypes(GetAgreementTermsResponse agreementTerm) {
    	Set<String> agreementTermTypes = new HashSet<String>();
    	try {
    		for ( AcceptedTerm term : agreementTerm.acceptedTerms()) {
    			ObjectMapper objectMapper = new ObjectMapper();
    	        JsonNode termNode = objectMapper.readTree(getJson(term));
    	        Iterator<Map.Entry<String, JsonNode>> fieldsIterator = termNode.fields();
                while (fieldsIterator.hasNext()) {
                    Map.Entry<String, JsonNode> entry = fieldsIterator.next();
                    JsonNode value = entry.getValue();
                    if (value.isObject() && value.has("type")) {
                    	System.out.println("type = " + value.get("type"));
                    	agreementTermTypes.add(value.get("type").asText());
                    }
                }
    		}
        } catch (Exception e) {
            e.printStackTrace();
        }
		return agreementTermTypes;
    	
    }
    
    //make sure all elements in array2 exist in array1
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
    
    public static Set<String> getMatchedTermTypesCombination(Set<String> agreementTermTypes) {
    	Set<String> matchedCombination = new HashSet<String>();
    	for ( Set<String> element : allAgreementTypesCombination) {
    		if ( allElementsExist(agreementTermTypes,element)) {
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
			Set<String> offerTermTypes = getOfferTermTypes(offerId);
			String prodType = summary.proposalSummary().resources().get(0).type();
			GetAgreementTermsRequest agreementTermsRequest = GetAgreementTermsRequest.builder()
					.agreementId(agreementId)
					.build();
			GetAgreementTermsResponse result = mpasClient.getAgreementTerms(agreementTermsRequest);
			Set<String> agreementTermTypes = getAgreementTermTypes(result);
			Set<String> matchedTermType = getMatchedTermTypesCombination(agreementTermTypes);
			String needToCheckOfferType = needToCheckOfferTermsType(prodType,matchedTermType);
			if ( needToCheckOfferType != null ) {
				Set<String> offerMatchedTermType = getMatchedTermTypesCombination(offerTermTypes);
				pricingType = getPricingType(prodType, matchedTermType, offerMatchedTermType);
			} else if (matchedTermType == legal ) {
				pricingType = Free;
			} else {
				pricingType = getPricingType(prodType, matchedTermType, new HashSet());
			}
			System.out.println("Pricing type is = " + pricingType);
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
