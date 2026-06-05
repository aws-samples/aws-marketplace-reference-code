
# AWS Marketplace API Reference Code Library - Java 

## How to use the reference code examples

You will need to have [Java 17](https://www.oracle.com/java/technologies/javase/jdk17-archive-downloads.html/) installed.

Before running this Java V2 code example, set up your development environment, including your credentials.
For more information, see the following documentation topic:
https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/get-started.html

### Change directories into the java source code folder:
```
cd aws-marketplace-reference-code/java
```

### Import the project into eclipse or your java IDE as maven project.

### Execute the following maven command. It will download all the required jars

```
mvn clean compile assembly:single 
```

### All sample changesets are inside resources folder

### To run against one particular changeset, run RunChangesets.java as a java application by changing the changeset name inside the java file; or run with the changeset file path as the input parameter.

### To run the code inside your IDE, add the resources folder to your build path -> source.

## Catalog API reference code

| Use case                                                                                                                                                                                                                                                                                             |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Create an AMI draft product with a draft public offer](./resources/changeSets/products/ami/CreateDraftAmiProductWithDraftPublicOffer.json)                                                                                                                                                          |
| [Create a container draft product with a draft public offer](./resources/changeSets/products/container/CreateDraftContainerProductWithDraftPublicOffer.json)                                                                                                                                         |
| [Create a SaaS draft product with a draft public offer](./resources/changeSets/products/saas/CreateSaasProductWithPublicOffer.json)                                                                                                                                                                  |
| [Publish my SaaS product and associated public offer (product will be in limited state by default)](./resources/changeSets/products/saas/PublishSaasProductPublicOffer.json)                                                                                                                         |
| [Publish my SaaS product and associated public offer (product will be in limited state by default)](./resources/changeSets/products/saas/PublishExistingSaas.json)                                                                                                                                   |
| [Create a public or limited AMI product and public offer with hourly annual pricing and standard or custom EULA](./resources/changeSets/products/ami/CreateLimitedAmiProductAndPublicOfferWithHourlyAnnualPricing.json)                                                                              |
| [Create a public or limited AMI product and public offer with hourly pricing and standard or custom EULA](./resources/changeSets/products/ami/CreateLimitedAmiProductAndPublicOfferWithHourlyPricing.json)                                                                                           |
| [Create a public or limited AMI product and public offer with hourly monthly pricing and standard or custom EULA](./resources/changeSets/products/ami/CreateLimitedAmiProductAndPublicOfferWithHourlyMonthlyPricing.json)                                                                            |
| [Create a public or limited SaaS product and public offer with subscription(usage) pricing and standard or custom EULA](./resources/changeSets/products/saas/CreateLimitedSaasAndPublicOfferWithSubscriptionPricing.json)                                                                            |
| [Create a public or limited SaaS product and public offer with contract with PAYG pricing and standard or custom EULA](./resources/changeSets/products/saas/CreateLimitedSaasAndPublicOfferWithContractWithPayAsYouGoPricing.json)                                                                   |
| [Create a public or limited SaaS product and public offer with contract pricing and standard or custom EULA](./resources/changeSets/products/saas/CreateLimitedSaasAndPublicOfferWithContractPricing.json)                                                                                           |
| [Create public free trial offer with subscription pricing for SaaS product](./resources/changeSets/offers/CreatePublicFreeTrialOfferWithSubscriptionPricingForSaas.json)                                                                                                                             |
| [Change free trial duration of public free trial offer for SaaS product](./resources/changeSets/offers/UpdateFreeTrialDurationOfPublicFreeTrialOfferForSass.json)                                                                                                                                    |
| [Create limited container product with public offer, contract pricing and standard EULA](./resources/changeSets/products/container/CreateLimitedContainerProductPublicOffer.json)                                                                                                                    |
| [Make your AMI or SaaS or Container product restricted](./resources/changeSets/products/ami/RestrictExistingAmi.json)                                                                                                                                                                                |
| [Update name and description of my public offer](./resources/changeSets/offers/UpdateEula.json)                                                                                                                                                                                                      |
| [Update EULA of my public offer](./resources/changeSets/offers/UpdateOfferNameAndDescription.json)                                                                                                                                                                                                   |
| [Update refund policy of my public offer](./resources/changeSets/offers/UpdateRefundPolicy.json)                                                                                                                                                                                                     |
| [Update geo-targeting of my public offer to specifically target few countries (e.g US/Canada/Spain) so that only customers in that region can subscribe to my offer](./resources/changeSets/offers/UpdateOfferTargeting.json)                                                                        |
| [Update price of my public offer for my AMI product with hourly annual pricing](./resources/changeSets/offers/UpdateOfferWithHourlyAnnualPricing.json)                                                                                                                                               |
| [Update price of my public offer for my SaaS product with contract and PAYG pricing](./resources/changeSets/offers/UpdateOfferWithContractAndPayAsYouGoPricing.json)                                                                                                                                 |
| [Add a new dimension to an AMI product and set the hourly price for this new dimension in the public offer](./resources/changeSets/products/ami/AddDimensionToAmiProductAndSetPriceInPublicOffer.json)                                                                                               |
| [Update (e.g name) dimensions on my AMI or SaaS product](./resources/changeSets/products/saas/UpdateNameDimensionSaasProduct.json)                                                                                                                                                                   |
| [Add a region where my AMI product is deployed](./resources/changeSets/products/ami/AddRegionExistingAmiProduct.json)                                                                                                                                                                                |
| [Restrict a region where my AMI product is deployed](./resources/changeSets/products/ami/RestrictRegionExistingAmiProduct.json)                                                                                                                                                                      |
| [Specify if I want my AMI assets to be deployed in new regions built by AWS (future region support)](./resources/changeSets/products/ami/UpdateFutureRegionSupport.json)                                                                                                                             |
| [List all my AMI or SaaS or Container products and associated public offers](./src/main/java/com/example/awsmarketplace/catalogapi/ListEntities.java)                                                                                                                                                |
| [Describe my AMI or SaaS or Container product and check if it contains all the information I need to know about the product](./src/main/java/com/example/awsmarketplace/catalogapi/DescribeEntity.java)                                                                                              |
| [Describe my public offer and check if it contains all the information I need to know about the offer](./src/main/java/com/example/awsmarketplace/catalogapi/DescribeEntity.java)                                                                                                                    |
| [Create draft private offers for my AMI or SaaS product so I can review them internally before publishing to my buyers](./resources/changeSets/offers/CreateDraftPrivateOffer.json)                                                                                                                  |
| [Create a private offer with hourly annual pricing for my AMI product and add a custom EULA](./resources/changeSets/offers/CreatePrivateOfferWithHourlyAnnualPricingForAmiProduct.json)                                                                                                              |
| [Create a private offer with hourly pricing for my AMI product](./resources/changeSets/offers/CreatePrivateOfferWithHourlyPricingForAmi.json)                                                                                                                                                        |
| [Create a private offer with contract pricing for my AMI product](./resources/changeSets/offers/CreatePrivateOfferWithContractPricingForAmiProduct.json)                                                                                                                                             |
| [Create a private offer (target buyers)for my Container product with contract pricing](./resources/changeSets/offers/CreatePrivateOfferWithContractPricingForContainerProduct.json)                                                                                                                  |
| [List all my private offers and sort or filter them by Offer Publish Date, Offer Expiry Date and Buyer IDs](./src/main/java/com/example/awsmarketplace/catalogapi/ListAllPrivateOffers.java)                                                                                                         |
| [Create draft resale authorization for any product type (AMI/SaaS/Container) so I can review them internally before publishing to my CPs](./resources/changeSets/resaleAuthorization/DraftResaleauthAllProductType.json)                                                                             |
| [Publish a one-time resale authorization on my SaaS product so my CP can use that to create Channel Partner Private Offer (CPPO)](./resources/changeSets/resaleAuthorization/OnetimeResaleauthPrivateoffer.json)                                                                                     |
| [Publish one-time resale authorization for any product type (AMI/SaaS/Container) and add a custom EULA to be sent to the buyer](./resources/changeSets/resaleAuthorization/OnetimeResaleauthCustomEula.json)                                                                                         |
| [Publish one-time resale authorization for any product type (AMI/SaaS/Container) and add reseller contract documentation between the ISV and CP](./resources/changeSets/resaleAuthorization/OnetimeResaleauthCustomresellerContractdoc.json)                                                         |
| [Publish multi-use resale authorization with expiry date for my AMI product with hourly annual pricing so my CP can use that to create CPPO](./resources/changeSets/resaleAuthorization/MultiuseResaleauthExpirydateCPPO.json)                                                                       |
| [Publish multi-use resale authorization without expiry date for my AMI product with hourly annual pricing so my CP can use that to create CPPO](./resources/changeSets/resaleAuthorization/MultiuseResaleautoNoExpirydateCPPO.json)                                                                  |
| [Publish multi-use resale authorization with expiry date for any product type (AMI/SaaS/Container) and add a custom EULA to be sent to the buyer](./resources/changeSets/resaleAuthorization/MultiuseResaleauthExpirydateCustomEula.json)                                                            |
| [Publish multi-use resale authorization with expiry date for any product type (AMI/SaaS/Container) and add reseller contract documentation between the ISV and CP](./resources/changeSets/resaleAuthorization/MultiuseResaleauthExpirydateCustomresellerContractdoc.json)                            |
| [Publish multi-use resale authorization without expiry date for any product type (AMI/SaaS/Container) and add a custom EULA to be sent to the buyer](./resources/changeSets/resaleAuthorization/MultiuseResaleauthNoExpirdateCustomEula.json)                                                        |
| [Publish multi-use resale authorization without expiry date for any product type (AMI/SaaS/Container) and add reseller contract documentation between the ISV and CP](./resources/changeSets/resaleAuthorization/MultiuseResaleauthNoExpirydateCustomResellerContractdoc.json)                       |
| [Create draft CPPO for any product type (AMI/SaaS/Container) so I can review them internally before publishing to my buyers](./resources/changeSets/channel_partner_offers/CreateDraftCppoOffer.json)                                                                                                |
| [Publish CPPO using one-time resale authorization on AMI, SaaS, or Container products and update price markup](./resources/changeSets/channel_partner_offers/PublishCppoPiceMarkupObject.json)                                                                                                       |
| [Publish CPPO using one-time resale authorization on any product type (AMI/SaaS/Container) and append buyer EULA with what was received from ISV](./resources/changeSets/channel_partner_offers/PublishCppoEula.json)                                                                                |
| [Update the offer expiry date of a CPPO I created to a date in future so my buyers get more time to evaluate and accept the offer](./resources/changeSets/channel_partner_offers/UpdateCppoExpiryDate.json)                                                                                          |
| [Publish CPPO using multi-use resale authorization with expiry date on AMI products and update price markup](./resources/changeSets/channel_partner_offers/PublishCppoPiceMarkupObject.json)                                                                                                         |
| [Publish CPPO using multi-use resale authorization with expiry date on SaaS products and update price markup](./resources/changeSets/channel_partner_offers/PublishCppoPiceMarkupObject.json)                                                                                                        |
| [Publish CPPO using multi-use resale authorization with expiry date on Container products and update price markup](./resources/changeSets/channel_partner_offers/PublishCppoPiceMarkupObject.json)                                                                                                   |
| [Publish CPPO using multi-use resale authorization with expiry date on any product type (AMI/SaaS/Container) and append buyer EULA with what was received from ISV](./resources/changeSets/channel_partner_offers/PublishCppoEula.json)                                                              |
| [Publish more than one CPPO using multi-use resale authorization with or without expiry date on any product type (AMI/SaaS/Container) and update price markup](./resources/changeSets/channel_partner_offers/PublishCppoPiceMarkupObject.json)                                                       |
| [Publish CPPO using multi-use resale authorization without expiry date on AMI products and update price markup](./resources/changeSets/channel_partner_offers/PublishCppoPiceMarkupObject.json)                                                                                                      |
| [Publish CPPO using multi-use resale authorization without expiry date on SaaS products and update price markup](./resources/changeSets/channel_partner_offers/PublishCppoPiceMarkupObject.json)                                                                                                     |
| [Publish CPPO using multi-use resale authorization without expiry date on Container products and update price markup](./resources/changeSets/channel_partner_offers/PublishCppoPiceMarkupObject.json)                                                                                                |
| [Publish CPPO using multi-use resale authorization without expiry date on any product type (AMI/SaaS/Container) and append buyer EULA with what was received from ISV](./resources/changeSets/channel_partner_offers/PublishCppoEula.json)                                                           |
| [Update name/description of one-time or multi-use resale authorization before publishing for any product type (AMI/SaaS/Container)](./resources/changeSets/resaleAuthorization/UpdateUnpublishedResaleAuthorization.json)                                                                            |
| [Publish one-time resale authorization for any product type (AMI/SaaS/Container) and add Flexible payment schedule](./resources/changeSets/resaleAuthorization/PublishOnetimeResaleAuthFlexiblePayment.json)                                                                                         |
| [Publish one-time resale authorization for any product type (AMI/SaaS/Container) and add specific buyer account for the resale](./resources/changeSets/resaleAuthorization/PublishOnetimeResaleAuthSpecificBuyer.json)                                                                               |
| [Publish multi-use resale authorization with expiry date for any product type (AMI/SaaS/Container) and add specific buyer account for the resale](./resources/changeSets/resaleAuthorization/PublishMultiuseResaleAuthExpirydateSpecificBuyer.json)                                                  |
| [Publish multi-use resale authorization without expiry date for any product type (AMI/SaaS/Container) and add specific buyer account for the resale](./resources/changeSets/resaleAuthorization/PublishMultiuseResaleAuthNoExpirydateSpecificBuyer.json)                                             |
| [Restrict a one-time resale authorization for any product type (AMI/SaaS/Container)](./resources/changeSets/resaleAuthorization/RestrictResaleAuthorization.json)                                                                                                                                    |
| [Publish one-time resale authorization for any product type (AMI/SaaS/Container) and add whether it is renewal or not](./resources/changeSets/resaleAuthorization/OnetimeResaleauthRenewal.json)                                                                                                     |
| [Create a custom dimension for an existing SaaS product and create a private offer](./resources/changeSets/offers/CreateSaasProductCustomDimensionAndPrivateOffer.json)                                                                                                                              |
| [Describe a resale authorization](./src/main/java/com/example/awsmarketplace/catalogapi/DescribeEntity.java)                                                                                                                                                                                         |
| [List all CPPOs created by a channel partner](./src/main/java/com/example/awsmarketplace/catalogapi/ListAllCppoOffers.java)                                                                                                                                                                          |
| [List all shared resale authorizations available to a channel partner](./src/main/java/com/example/awsmarketplace/catalogapi/ListAllSharedResaleAuthorizations.java)                                                                                                                                 |
| [Create a replacement private offer from an existing agreement with contract pricing](./resources/changeSets/offers/CreateReplacementPrivateOfferWithContractPricing.json)                                                                                                                           |
| [Create a resale authorization replacement private offer from an existing agreement with contract pricing](./resources/changeSets/channel_partner_offers/CreateResaleAuthorizationReplacementOffer.json)                                                                                             |
| [List and describe all private Offers associated with a product](./src/main/java/com/example/awsmarketplace/catalogapi/ListProductPrivateOffers.java)                                                                                                                                                |
| [List released Public/Private offers for a specific product id](./src/main/java/com/example/awsmarketplace/catalogapi/ListProductPublicOrPrivateReleasedOffers.java)                                                                                                                                 |
| [BatchDescribe my entities in a single call and check if it contains all the information I need to know about the entities](./src/main/java/com/example/awsmarketplace/catalogapi/BatchDescribeEntities.java) |

## Agreement API reference code

### Seller use cases

|Use case|
|--------|
|[Obtain a list of all of my agreements](./src/main/java/com/example/awsmarketplace/agreementapi/seller/GetAllAgreements.java)|
|[Filter my agreements based on product ID, Customer AWS Account ID, Offer ID](./src/main/java/com/example/awsmarketplace/agreementapi/seller/SearchAgreementsByOneFilter.java)|
|[Filter my agreements based on product ID](./src/main/java/com/example/awsmarketplace/agreementapi/seller/SearchAgreementsByOneFilter.java)|
|[Filter my agreements based on AWS Account ID](./src/main/java/com/example/awsmarketplace/agreementapi/seller/SearchAgreementsByOneFilter.java)|
|[Filter my agreements based on Offer ID](./src/main/java/com/example/awsmarketplace/agreementapi/seller/SearchAgreementsByOneFilter.java)|
|[Filter my agreements based on whether its end date is before or after a date I can specify (such as today)](./src/main/java/com/example/awsmarketplace/agreementapi/seller/SearchAgreementsByEndDate.java)|
|[Filter my agreements based on status](./src/main/java/com/example/awsmarketplace/agreementapi/seller/SearchAgreementsByOneFilter.java)|
|[Filter my agreement based on its product type](./src/main/java/com/example/awsmarketplace/agreementapi/seller/SearchAgreementsByOneFilter.java)|
|[Filter my agreement based on a combination of any of the above filters](./src/main/java/com/example/awsmarketplace/agreementapi/seller/SearchAgreementsByTwoFilters.java)|
|[Obtain metadata about my agreement, like its sign date, start date or end date](./src/main/java/com/example/awsmarketplace/agreementapi/seller/DescribeAgreement.java)|
|[Obtain metadata about the customer who created the agreement, such as the customer's AWS Account ID](./src/main/java/com/example/awsmarketplace/agreementapi/seller/GetAgreementCustomerInfo.java)|
|[Obtain all the Agreement IDs](./src/main/java/com/example/awsmarketplace/agreementapi/seller/GetAllAgreementsIds.java)|
|[Obtain information about the product and offer that the agreement was created on such as Product ID and Offer ID](./src/main/java/com/example/awsmarketplace/agreementapi/seller/GetProductAndOfferDetailFromAgreement.java)|
|[Obtain the Product Type of the product the agreement was created on](./src/main/java/com/example/awsmarketplace/agreementapi/seller/GetAgreementProductType.java)|
|[Retrieve the status of the agreement](./src/main/java/com/example/awsmarketplace/agreementapi/seller/GetAgreementStatus.java)|
|[Obtain financial details, such as Total Contract Value of the agreement](./src/main/java/com/example/awsmarketplace/agreementapi/seller/GetAgreementFinancialDetails.java)|
|[Obtain the auto-renewal status of the agreement](./src/main/java/com/example/awsmarketplace/agreementapi/seller/GetAgreementAutoRenewal.java)|
|[Obtain the pricing type of the agreement (contract, FPS, metered, free etc.)](./src/main/java/com/example/awsmarketplace/agreementapi/seller/GetAgreementPricingType.java)|
|[Obtain the payment schedule I have agreed to with the agreement, including the invoice date and invoice amount](./src/main/java/com/example/awsmarketplace/agreementapi/seller/GetAgreementTermsPaymentSchedule.java)|
|[Obtain the EULA I have entered into with my customer via the agreement](./src/main/java/com/example/awsmarketplace/agreementapi/seller/GetAgreementTermsEula.java)|
|[Obtain the support and refund policy I have provided to the customer](./src/main/java/com/example/awsmarketplace/agreementapi/seller/GetAgreementTermsSupportTerm.java)|
|[Obtain the details from an agreement of a free trial I have provided to the customer](./src/main/java/com/example/awsmarketplace/agreementapi/seller/GetAgreementTermsFreeTrialDetails.java)|
|[Obtain the dimensions the buyer has purchased from me via the agreement](./src/main/java/com/example/awsmarketplace/agreementapi/seller/GetAgreementTermsDimensionPurchased.java)|
|[Obtain pricing per each dimension in the agreement](./src/main/java/com/example/awsmarketplace/agreementapi/seller/GetAgreementTermsPricingEachDimension.java)|
|[Obtain instances of each dimension that buyer has purchased in the agreement](./src/main/java/com/example/awsmarketplace/agreementapi/seller/GetAgreementTermsDimensionInstances.java)|

### Buyer use cases

|Use case|
|--------|
|[Amend an AMI agreement with ConfigurableUpfrontPricingTerm by updating dimension quantity for usage pricing model](./src/main/java/com/example/awsmarketplace/agreementapi/buyer/AmendAmiConfigurableUpfrontPricingTermForUsagePricingModel.java)|
|[Amend a SaaS contract agreement to add or update its renewal term](./src/main/java/com/example/awsmarketplace/agreementapi/buyer/AmendSaaSContractRenewalTerm.java)|
|[Create a new AMI free trial agreement](./src/main/java/com/example/awsmarketplace/agreementapi/buyer/NewAmiFreeTrial.java)|
|[Create a new SaaS contract agreement with upfront payment](./src/main/java/com/example/awsmarketplace/agreementapi/buyer/NewSaaSContractWithUpfrontPayment.java)|
|[Replace an AMI usage-based pricing term but keep the existing ConfigurableUpfrontPricingTerm](./src/main/java/com/example/awsmarketplace/agreementapi/buyer/ReplaceAmiUsageBasedPricingTermButNotCupt.java)|
|[Replace a SaaS contract agreement with a new agreement-based offer](./src/main/java/com/example/awsmarketplace/agreementapi/buyer/ReplaceSaaSContractWithAgreementBasedOffer.java)|
|[Replace a SaaS free trial with a Contract with Consumption Pricing (CCP)](./src/main/java/com/example/awsmarketplace/agreementapi/buyer/ReplaceSaaSFreeTrialWithCCP.java)|
|[Replace a SaaS usage-based pricing term and cancel the previous agreement](./src/main/java/com/example/awsmarketplace/agreementapi/buyer/ReplaceSaaSUsageBasedPricingTermAndCancel.java)|
|[Update purchase orders after the agreement has been accepted](./src/main/java/com/example/awsmarketplace/agreementapi/buyer/UpdatePurchaseOrdersAfterAgreementAcceptance.java)|
|[Accept an agreement cancellation request initiated by the seller](./src/main/java/com/example/awsmarketplace/agreementapi/buyer/agreementCancellation/AcceptAgreementCancellationRequest.java)|
|[Get details of a specific agreement cancellation request](./src/main/java/com/example/awsmarketplace/agreementapi/buyer/agreementCancellation/GetAgreementCancellationRequest.java)|
|[List all agreement cancellation requests for agreements I participate in as acceptor](./src/main/java/com/example/awsmarketplace/agreementapi/buyer/agreementCancellation/ListAgreementCancellationRequests.java)|
|[Reject an agreement cancellation request initiated by the seller](./src/main/java/com/example/awsmarketplace/agreementapi/buyer/agreementCancellation/RejectAgreementCancellationRequest.java)|
|[Accept an agreement payment request initiated by the seller](./src/main/java/com/example/awsmarketplace/agreementapi/buyer/paymentRequest/AcceptAgreementPaymentRequest.java)|
|[Get details of a specific agreement payment request](./src/main/java/com/example/awsmarketplace/agreementapi/buyer/paymentRequest/GetAgreementPaymentRequest.java)|
|[List all agreement payment requests for agreements I participate in as acceptor](./src/main/java/com/example/awsmarketplace/agreementapi/buyer/paymentRequest/ListAgreementPaymentRequests.java)|
|[Reject an agreement payment request initiated by the seller](./src/main/java/com/example/awsmarketplace/agreementapi/buyer/paymentRequest/RejectAgreementPaymentRequest.java)|

### Submit defects & questions
If you find any defects with the APIs, need help troubleshooting, or have general questions or feedback, [use this form to contact us](https://aws.amazon.com/marketplace/management/contact-us/)


## AWS SDK for Java

Get started quickly using AWS in java, the AWS SDK for Java makes it easy to integrate your Java application, library, or script with AWS services including Amazon S3, Amazon EC2, Amazon DynamoDB, and more.

https://aws.amazon.com/sdk-for-java/

## AWS Marketplace Documentation

To access detailed AWS Marketplace API documentation:

https://docs.aws.amazon.com/marketplace/

