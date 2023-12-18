package com.example.awsmarketplace.catalogapi.Entity;

import com.fasterxml.jackson.annotation.JsonProperty;

public class ChangeSet {
	@JsonProperty("ChangeType")
	public String ChangeType;
	@JsonProperty("Entity")
	public ChangeSetEntity Entity;
	@JsonProperty("ChangeName")
	public String ChangeName;
	@JsonProperty("Details")
	public String Details;
	@JsonProperty("DetailsDocument")
	public Object DetailsDocument;
}