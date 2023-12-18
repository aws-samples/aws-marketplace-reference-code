package com.example.awsmarketplace.catalogapi.Entity;

import com.fasterxml.jackson.annotation.JsonProperty;

public class ChangeSetEntity {
	@JsonProperty("Type")
	public String Type;
	@JsonProperty("Identifier")
	public String Identifier;
}