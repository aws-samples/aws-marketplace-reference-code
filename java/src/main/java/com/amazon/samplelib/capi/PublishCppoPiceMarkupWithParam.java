package com.amazon.samplelib.capi;

import java.io.ByteArrayInputStream;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.io.IOUtils;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;
import com.fasterxml.jackson.annotation.JsonProperty;

import com.google.gson.Gson;
import com.google.gson.annotations.SerializedName;

import software.amazon.awssdk.services.marketplacecatalog.MarketplaceCatalogClient;
import software.amazon.awssdk.services.marketplacecatalog.model.Change;
import software.amazon.awssdk.services.marketplacecatalog.model.Entity;
import software.amazon.awssdk.services.marketplacecatalog.model.StartChangeSetRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.StartChangeSetResponse;

public class PublishCppoPiceMarkupWithParam {

	public static void main(String[] args) {

		int numberOfCppo = 1;
		String inputJson = "changeset.json";
		
		final String RESALE_ID = ReferenceCodesConstants.RESALEAUTHORIZATION_ID;
		final String PERCENTAGE = "5.0";
		final String BUYER_ACCOUNT_1 = ReferenceCodesConstants.BUYER_ACCOUNT_ID;
		final String AVAIL_END_DATE = "2023-07-31";
		final String AGREEMENT_DURATION= "P450D";
		

		Gson gson = new Gson();
		List<Change> changeSetLists = new ArrayList<Change>();
		try {
			String changeSetsInput = IOUtils
					.toString(PublishCppoPiceMarkupWithParam.class.getResourceAsStream(inputJson), "UTF-8").trim()
					.replace('\n', ' ');
			String changeSetsInputWithParam = String.format(changeSetsInput, RESALE_ID, PERCENTAGE,BUYER_ACCOUNT_1, AVAIL_END_DATE, AGREEMENT_DURATION );
			
			
			Root root = gson.fromJson(changeSetsInputWithParam, Root.class);
			ArrayList<ChangeSet> allChangeSets = root.changeSet;
			for (ChangeSet cs : allChangeSets) {
				ChangeSetEntity entity = cs.Entity;
				String entityType = entity.Type;
				String entityIdentifier = entity.Identifier;
				Object details = cs.Details;

				Entity awsEntity = Entity.builder()
						.type(entityType)
						.identifier(entityIdentifier != null && entityIdentifier.length() > 0 ? entityIdentifier : null)
						.build();
				
				String detailString = IOUtils.toString(new ByteArrayInputStream(gson.toJson(details).getBytes()), "UTF-8").trim().replace('\n', ' ');
				
				Change inputChangeRequest = Change.builder().changeType(cs.ChangeType)
						.changeName(cs.ChangeName).entity(awsEntity).details(detailString != null && detailString.length() > 0 && !detailString.contains("{}") ? detailString : "{}")
						.build();
				
				changeSetLists.add(inputChangeRequest);

			}

			StartChangeSetRequest request = StartChangeSetRequest.builder().catalog(root.catalog)
					.changeSet(changeSetLists).build();

			MarketplaceCatalogClient awsMarketplaceCatalog = ReferenceCodesUtils.getMPCatalogClient();

			for (int i = 0; i < numberOfCppo; i++) {
				StartChangeSetResponse result = awsMarketplaceCatalog.startChangeSet(request);
		        ReferenceCodesUtils.printResult(result);
			}

		} catch (Exception e) {
			e.printStackTrace();
		}

	}

	public class ChangeSet {
		@JsonProperty("ChangeType")
		public String ChangeType;
		@JsonProperty("Entity")
		public ChangeSetEntity Entity;
		@JsonProperty("ChangeName")
		public String ChangeName;
		@JsonProperty("DetailsDocument")
		public Object Details;
	}

	public class ChangeSetEntity {
		@JsonProperty("Type")
		public String Type;
		@JsonProperty("Identifier")
		public String Identifier;
	}

	public class Root {
		@SerializedName(value = "catalog", alternate = "Catalog")
		public String catalog;
		public ArrayList<ChangeSet> changeSet;
	}

}
