// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
package com.amazon.samplelib;

import com.fasterxml.jackson.annotation.PropertyAccessor;
import com.fasterxml.jackson.annotation.JsonAutoDetect.Visibility;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

import software.amazon.awssdk.auth.credentials.ProfileCredentialsProvider;
import software.amazon.awssdk.core.ResponseBytes;
import software.amazon.awssdk.http.apache.ApacheHttpClient;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.GetObjectResponse;
import software.amazon.awssdk.services.ssm.SsmClient;
import software.amazon.awssdk.services.ssm.model.ParameterType;
import software.amazon.awssdk.services.ssm.model.PutParameterRequest;
import software.amazon.awssdk.services.ssm.model.GetParameterRequest;
import software.amazon.awssdk.services.ssm.model.GetParameterResponse;
import software.amazon.awssdk.services.ssm.model.SsmException;

public class Helpers {
	
	static Region region = Region.US_EAST_1;
    static SsmClient ssmClient = SsmClient.builder()
    		.httpClient(ApacheHttpClient.builder().build())
    		.credentialsProvider(ProfileCredentialsProvider.create())
            .region(region)
            .build();
    static S3Client s3Client = S3Client.builder()
    		.httpClient(ApacheHttpClient.builder().build())
    		.credentialsProvider(ProfileCredentialsProvider.create())
            .region(region)
            .build();
    
    public static String getJsonStringFromS3Bucket(String bucketName, String fileKey) {
    	String jsonString = "";
    	try {
            GetObjectRequest getObjectRequest = GetObjectRequest.builder()
                    .bucket(bucketName)
                    .key(fileKey)
                    .build();

            ResponseBytes<GetObjectResponse> objectBytes = s3Client.getObjectAsBytes(getObjectRequest);
            jsonString = objectBytes.asUtf8String();
        } catch (Exception e) {
            e.printStackTrace();
        }
    	return jsonString;
    }

	public static void formatOutput(Object result) {
		try {
			ObjectMapper om = new ObjectMapper();
			om.configure(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS, false);
			om.setVisibility(PropertyAccessor.FIELD, Visibility.ANY);
			om.registerModule(new JavaTimeModule());
			ObjectWriter ow = om.writer().withDefaultPrettyPrinter();

			String json = ow.writeValueAsString(result);
			System.out.println(json);
		} catch (JsonProcessingException e) {
			e.printStackTrace();
		}
	}
	
	 public static void createParameter(String paraName, String value) {
	        try {
	            PutParameterRequest parameterRequest = PutParameterRequest.builder()
	                    .name(paraName)
	                    .type(ParameterType.STRING)
	                    .value(value)
	                    .build();

	            ssmClient.putParameter(parameterRequest);
	            System.out.println("The parameter was successfully added.");

	        } catch (SsmException e) {
	            System.err.println(e.getMessage());
	            System.exit(1);
	        }
	    }
	
	 public static String getParameterValue(String paraName) {
		 	String parameterValue = "";
	        try {
	            GetParameterRequest parameterRequest = GetParameterRequest.builder()
	                    .name(paraName)
	                    .build();

	            GetParameterResponse parameterResponse = ssmClient.getParameter(parameterRequest);
	            parameterValue = parameterResponse.parameter().value();
	            System.out.println("The parameter value is " + parameterValue);
	        } catch (SsmException e) {
	            System.err.println(e.getMessage());
	            System.exit(1);
	        }
	        return parameterValue;
	  }
	 
	 
}
