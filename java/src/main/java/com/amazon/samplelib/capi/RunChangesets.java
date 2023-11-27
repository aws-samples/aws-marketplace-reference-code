package com.amazon.samplelib.capi;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.io.IOUtils;

import software.amazon.awssdk.core.document.Document;
import software.amazon.awssdk.protocols.json.internal.unmarshall.document.DocumentUnmarshaller;
import software.amazon.awssdk.protocols.jsoncore.JsonNodeParser;
import software.amazon.awssdk.services.marketplacecatalog.model.Change;
import software.amazon.awssdk.services.marketplacecatalog.model.Entity;
import software.amazon.awssdk.services.marketplacecatalog.model.StartChangeSetRequest;
import software.amazon.awssdk.services.marketplacecatalog.model.StartChangeSetResponse;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.ToNumberPolicy;
import com.amazon.samplelib.Entity.ChangeSet;
import com.amazon.samplelib.Entity.ChangeSetEntity;
import com.amazon.samplelib.Entity.Root;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

public class RunChangesets {

	private static Gson gson = new GsonBuilder().setObjectToNumberStrategy(ToNumberPolicy.LAZILY_PARSED_NUMBER).create();
	private static final JsonNodeParser jsonNodeParser = JsonNodeParser.create();

	public static void main(String[] args) {

		// replace with your changeset name
		String inputJson = "changeSets/offers/CreateReplacementOfferFromAGWithContractPricingDetailDocument.json";

		if (args.length > 0)
			inputJson = args[0];

		try {
			StartChangeSetResponse result = getResult(inputJson);
			ReferenceCodesUtils.printResult(result);
		} catch (Exception e) {
			e.printStackTrace();
		}
	}

	private static StartChangeSetResponse getResult(String inputJson) throws IOException {

		List<Change> changeSetLists = new ArrayList<Change>();

		System.out.println("input json" + inputJson);
		InputStream is = RunChangesets.class.getClassLoader().getResourceAsStream(inputJson);
		
		if (is == null) {
			System.out.println("inputstream is null");
		}
		String changeSetsInput = IOUtils
				.toString(RunChangesets.class.getClassLoader().getResourceAsStream(inputJson), "UTF-8").trim()
				.replace('\n', ' ');

		Root root = gson.fromJson(changeSetsInput, Root.class);
		ArrayList<ChangeSet> allChangeSets = root.changeSet;

		getChangeSetList(changeSetLists, allChangeSets);

		StartChangeSetRequest startChangeSetRequest = StartChangeSetRequest.builder().catalog(root.catalog)
				.changeSet(changeSetLists).build();
		
		StartChangeSetResponse result = ReferenceCodesUtils.getMPCatalogClient().startChangeSet(startChangeSetRequest);
		
		return result;
	}

	private static void getChangeSetList(List<Change> changeSetLists, ArrayList<ChangeSet> allChangeSets)
			throws IOException {
		// loop through all the changesets and add the changeset list
		for (ChangeSet cs : allChangeSets) {
			ChangeSetEntity entity = cs.Entity;
			String entityType = entity.Type;
			String entityIdentifier = entity.Identifier;
			Object details = cs.DetailsDocument;
			boolean hasDetailDocument = true;
			if (details == null) {
				details = cs.Details;
				hasDetailDocument = false;
			}

			Entity awsEntity = Entity.builder().type(entityType)
					.identifier(entityIdentifier != null && entityIdentifier.length() > 0 ? entityIdentifier : null)
					.build();

			Change inputChangeRequest = null;

			if (hasDetailDocument) {
				inputChangeRequest = Change.builder().changeType(cs.ChangeType).changeName(cs.ChangeName)
						.entity(awsEntity).detailsDocument(getDocumentFromString(getDetailString(details))).build();
			} else {
				inputChangeRequest = Change.builder().changeType(cs.ChangeType).changeName(cs.ChangeName)
						.entity(awsEntity).details(getDetailString(details)).build();
			}
			changeSetLists.add(inputChangeRequest);
		}
	}

	private static String getDetailString(Object details) throws IOException {
		String detailString = IOUtils.toString(new ByteArrayInputStream(gson.toJson(details).getBytes()), "UTF-8")
				.trim().replace('\n', ' ');
		return detailString != null && detailString.length() > 0 && !detailString.contains("{}") ? detailString : "{}";
	}

	public static Document getDocumentFromString(String detailJsonString) {
			Document doc = jsonNodeParser.parse(detailJsonString).visit(new DocumentUnmarshaller());
	    	return doc;
	}
}
