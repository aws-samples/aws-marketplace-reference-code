//AG-17 Obtain the payment schedule I have agreed to with the agreement, including the invoice date and invoice amount
package com.amazon.samplelib.agreement;

import software.amazon.awssdk.services.marketplaceagreement.MarketplaceAgreementClient;
import software.amazon.awssdk.services.marketplaceagreement.model.AcceptedTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.PaymentScheduleTerm;
import software.amazon.awssdk.services.marketplaceagreement.model.ScheduleItem;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.amazon.samplelib.utils.ReferenceCodesConstants;
import com.amazon.samplelib.utils.ReferenceCodesUtils;

public class GetAgreementTermsPaymentSchedule {
	
	static String agreementId = ReferenceCodesConstants.AGREEMENT_ID;

	public static void main(String[] args) {
		
		MarketplaceAgreementClient mpasClient = ReferenceCodesUtils.getMPAgreementClient();

		List<AcceptedTerm> acceptedTerms = ReferenceCodesUtils.getAgreementAcceptedTerms(mpasClient, agreementId);
		
		List<Map<String, Object>> paymentScheduleArray = new ArrayList<>();
        
		String currencyCode = "";
        
		for (AcceptedTerm aterm : acceptedTerms) {
			if ( aterm.paymentScheduleTerm() != null ) {
				PaymentScheduleTerm paymentScheduleTerm = aterm.paymentScheduleTerm();
				if ( paymentScheduleTerm.currencyCode() != null) {
					currencyCode = paymentScheduleTerm.currencyCode();
				}
				if ( paymentScheduleTerm.hasSchedule()) {
					for (ScheduleItem schedule : paymentScheduleTerm.schedule()) {
						if ( schedule.chargeDate() != null ) {
							String chargeDate = schedule.chargeDate().toString();
                            String chargeAmount = schedule.chargeAmount();
                            Map<String, Object> scheduleMap = new HashMap<>();
                            scheduleMap.put("currencyCode", currencyCode);
                            scheduleMap.put("chargeDate", chargeDate);
                            scheduleMap.put("chargeAmount", chargeAmount);
	                        paymentScheduleArray.add(scheduleMap);
						}
					}
				}
			}
		}
		
		ReferenceCodesUtils.printResult(paymentScheduleArray);
	}
}
