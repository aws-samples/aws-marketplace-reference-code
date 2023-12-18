package com.example.awsmarketplace.catalogapi.Entity;

import java.util.ArrayList;

import com.google.gson.annotations.SerializedName;

public class Root {
	@SerializedName(value = "catalog", alternate = "Catalog")
	public String catalog;
	public ArrayList<ChangeSet> changeSet;
}