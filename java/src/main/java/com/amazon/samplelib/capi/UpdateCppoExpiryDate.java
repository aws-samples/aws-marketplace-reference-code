package com.amazon.samplelib.capi;

import java.io.IOException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import org.apache.commons.io.IOUtils;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

import software.amazon.awssdk.services.marketplacecatalog.MarketplaceCatalogClient;
import software.amazon.awssdk.services.marketplacecatalog.model.Change;
import software.amazon.awssdk.services.marketplacecatalog.model.Entity;
import software.amazon.awssdk.services.marketplacecatalog.model.StartChangeSetRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.StartChangeSetResponse;

public class UpdateCppoExpiryDate {

	public static void main(String[] args) {
		
		int daysInFuture = 365;
		
		String detailsAvailabilityString = "";
		
		String offerId = ReferenceCodesConstants.OFFER_ID;
		
		try {
			
			String availabilityStringFromFile = IOUtils.toString(UpdateCppoExpiryDate.class.getResourceAsStream("availabilityDate.json"), "UTF-8")
					.trim().replace('\n', ' ');
			
			LocalDate today = LocalDate.now();

	        // add the specified number of days
	        LocalDate newDate = today.plusDays(daysInFuture);

	        // format the new date as a string
	        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
	        String newDateString = newDate.format(formatter);

	        // create the new JSON string with the updated date
	        detailsAvailabilityString = availabilityStringFromFile.replaceFirst("(?<=\"AvailabilityEndDate\": \")\\d{4}-\\d{2}-\\d{2}", newDateString);

			
		} catch (IOException e) {
			e.printStackTrace();
		}
				
		MarketplaceCatalogClient awsMarketplaceCatalog = ReferenceCodesUtils.getMPCatalogClient();

		 
		Entity inputEntity = Entity.builder()
                .type("Offer@1.0")
                .identifier(offerId)
                .build();

        // update availability
        
        Change availabilityChangeRequest = Change.builder()
        		.changeType("UpdateAvailability")
        		.entity(inputEntity)
        		.details(detailsAvailabilityString)
        		.build();
        
        StartChangeSetRequest request = StartChangeSetRequest.builder()
                .catalog(ReferenceCodesConstants.AWS_MP_CATALOG)
                .changeSet(Arrays.asList(availabilityChangeRequest))
                .build();

        StartChangeSetResponse result = awsMarketplaceCatalog.startChangeSet(request);
        
        ReferenceCodesUtils.printResult(result);
 	}

}
