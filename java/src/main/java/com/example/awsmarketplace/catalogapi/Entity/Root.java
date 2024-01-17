package com.example.awsmarketplace.catalogapi.Entity;

import java.util.ArrayList;

import com.google.gson.annotations.SerializedName;

public class Root {
	@SerializedName(value = "catalog", alternate = "Catalog")
	public String catalog;
	@SerializedName(value = "changeSet", alternate = "ChangeSet")
	public ArrayList<ChangeSet> changeSet;
}