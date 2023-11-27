package com.amazon.samplelib.agreement;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.DescribeAgreementResponse;

public class GetAgreementCustomerInfo {
	
	static String agreementId = ReferenceCodesConstants.AGREEMENT_ID;

	public static void main(String[] args) {

		MarketplaceAgreementClient mpasClient = ReferenceCodesUtils.getMPAgreementClient();

		DescribeAgreementResponse result = ReferenceCodesUtils.getDescribeAgreementResult(mpasClient, agreementId);

		String acceptorId = result.acceptor().accountId();
		
		System.out.println("Customer id = " + acceptorId);
	
	}

}
