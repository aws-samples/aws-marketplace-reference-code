package com.example.awsmarketplace.catalogapi;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.io.IOUtils;
import org.apache.commons.lang3.StringUtils;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.core.document.Document;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.protocols.json.internal.unmarshall.document.DocumentUnmarshaller;
import software.amazon.awssdk.protocols.jsoncore.JsonNodeParser;
import software.amazon.awssdk.services.marketplacecatalog.MarketplaceCatalogClient;
import software.amazon.awssdk.services.marketplacecatalog.model.Change;
import software.amazon.awssdk.services.marketplacecatalog.model.Entity;
import software.amazon.awssdk.services.marketplacecatalog.model.StartChangeSetRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.StartChangeSetResponse;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.ToNumberPolicy;
import com.example.awsmarketplace.catalogapi.Entity.ChangeSet;
import com.example.awsmarketplace.catalogapi.Entity.ChangeSetEntity;
import com.example.awsmarketplace.catalogapi.Entity.Root;
import com.example.awsmarketplace.utils.ReferenceCodesUtils;
import com.example.awsmarketplace.utils.StringSerializer;

/**
 * Before running this Java V2 code example, convert all Details attribute to DetailsDocument if any
 */

public class RunChangesets {
	
	private static final Gson GSON = new GsonBuilder()
			.setObjectToNumberStrategy(ToNumberPolicy.LAZILY_PARSED_NUMBER)
			.registerTypeAdapter(String.class, new StringSerializer())
			.create();

	public static void main(String[] args) {

		// input json can be specified here or passed from input parameter
		String inputChangeSetFile = "changeSets/offers/CreateReplacementOfferFromAGWithContractPricingDetailDocument.json";
		
		if (args.length > 0)
			inputChangeSetFile = args[0];
		
		// parse the input changeset file to string for process
		String changeSetsInput = readChangeSetToString(inputChangeSetFile);

		// process the changeset request
		try {
			StartChangeSetResponse result = getChangeSetRequestResult(changeSetsInput);
			ReferenceCodesUtils.formatOutput(result);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	private static StartChangeSetResponse getChangeSetRequestResult(String changeSetsInput) throws IOException {
		
		//set up AWS credentials
		MarketplaceCatalogClient marketplaceCatalogClient = 
				MarketplaceCatalogClient.builder()
				.httpClient(ApacheHttpClient.builder().build())
				.credentialsProvider(ProfileCredentialsProvider.create())
				.build();
		
		//changeset list to save all the changesets in the changesets file
		List<Change> changeSetLists = new ArrayList<Change>();

		// read all changesets into object
		Root root = GSON.fromJson(changeSetsInput, Root.class);
		
		// process each changeset and add each changeset request to changesets list
		for (ChangeSet cs : root.changeSet) {
			
			ChangeSetEntity entity = cs.Entity;
			String entityType = entity.Type;
			String entityIdentifier = StringUtils.defaultIfBlank(entity.Identifier, null);
			Document detailsDocument = getDocumentFromObject(cs.DetailsDocument);
			
			Entity awsEntity = 
					Entity.builder()
					.type(entityType)
					.identifier(entityIdentifier)
					.build();

			Change inputChangeRequest = 
					Change.builder()
					.changeType(cs.ChangeType)
					.changeName(cs.ChangeName)
					.entity(awsEntity)
					.detailsDocument(detailsDocument)
					.build();
			
			changeSetLists.add(inputChangeRequest);
		}
		
		// process all changeset requests
		StartChangeSetRequest startChangeSetRequest = 
				StartChangeSetRequest.builder()
				.catalog(root.catalog)
				.changeSet(changeSetLists)
				.build();

		StartChangeSetResponse result = marketplaceCatalogClient.startChangeSet(startChangeSetRequest);

		return result;
	}

	public static Document getDocumentFromObject(Object detailsObject) {
		
		String detailsString = "{}";
		try {
			detailsString = IOUtils.toString(new ByteArrayInputStream(GSON.toJson(detailsObject).getBytes()), "UTF-8");
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		JsonNodeParser jsonNodeParser = JsonNodeParser.create();
		Document doc = jsonNodeParser.parse(detailsString).visit(new DocumentUnmarshaller());
		return doc;
	}
	
	
	private static String readChangeSetToString (String inputChangeSetFile) {
		
		InputStream changesetInputStream = RunChangesets.class.getClassLoader().getResourceAsStream(inputChangeSetFile);

		String changeSetsInput = null;
		
		try {
			changeSetsInput = IOUtils.toString(changesetInputStream, "UTF-8");
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		return changeSetsInput;
		
	}
}
