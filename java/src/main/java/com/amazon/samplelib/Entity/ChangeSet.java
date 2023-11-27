package com.amazon.samplelib.Entity;

import com.fasterxml.jackson.annotation.JsonProperty;

public class ChangeSet {
	@JsonProperty("ChangeType")
	public String ChangeType;
	@JsonProperty("Entity")
	public ChangeSetEntity Entity;
	@JsonProperty("ChangeName")
	public String ChangeName;
	@JsonProperty("Details")
	public Object Details;
	@JsonProperty("DetailsDocument")
	public Object DetailsDocument;
}