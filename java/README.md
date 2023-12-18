
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

## Catalog API reference code

|Id|Use case|
|-------|--------|
|capi-02|[Create an AMI draft product with a draft public offer](./resources/changeSets/products/ami/CreateDraftAmiProductWithDraftPublicOffer.json)|
|capi-03|[Create a container draft product with a draft public offer](./resources/changeSets/products/container/CreateDraftContainerProductWithDraftPublicOffer.json)|
|capi-04|[Create a SaaS draft product with a draft public offer](./resources/changeSets/products/saas/CreateSaasProductWithPublicOffer.json)|
|capi-05A|[Publish my SaaS product and associated public offer (product will be in limited state by default)](./resources/changeSets/products/saas/PublishSaasProductPublicOffer.json)|
|capi-05A|[Publish my SaaS product and associated public offer (product will be in limited state by default)](./resources/changeSets/products/saas/PublishExistingSaas.json)|
|capi-06|[Create a public or limited AMI product and public offer with hourly annual pricing and standard or custom EULA](./resources/changeSets/products/ami/CreateLimitedAmiProductAndPublicOfferWithHourlyAnnualPricing.json)|
|capi-07|[Create a public or limited AMI product and public offer with hourly pricing and standard or custom EULA](./resources/changeSets/products/ami/CreateLimitedAmiProductAndPublicOfferWithHourlyPricing.json)|
|capi-08|[Create a public or limited AMI product and public offer with hourly monthly pricing and standard or custom EULA](./resources/changeSets/products/ami/CreateLimitedAmiProductAndPublicOfferWithHourlyMonthlyPricing.json)|
|capi-09|[Create a public or limited SaaS product and public offer with subscription(usage) pricing and standard or custom EULA](./resources/changeSets/products/saas/CreateLimitedSaasAndPublicOfferWithSubscriptionPricing.json)|
|capi-10|[Create a public or limited SaaS product and public offer with contract with PAYG pricing and standard or custom EULA](./resources/changeSets/products/saas/CreateLimitedSaasAndPublicOfferWithContractWithPayAsYouGoPricing.json)|
|capi-11|[Create a public or limited SaaS product and public offer with contract pricing and standard or custom EULA](./resources/changeSets/products/saas/CreateLimitedSaasAndPublicOfferWithContractPricing.json)|
|capi-13|[Create public free trial offer with subscription pricing for SaaS product](./resources/changeSets/offers/CreatePublicFreeTrialOfferWithSubscriptionPricingForSaas.json)|
|capi-14|[Change free trial duration of public free trial offer for SaaS product](./resources/changeSets/offers/UpdateFreeTrialDurationOfPublicFreeTrialOfferForSass.json)|
|capi-15|[Create limited container product with public offer, contract pricing and standard EULA](./resources/changeSets/products/container/CreateLimitedContainerProductPublicOffer.json)|
|capi-17|[Make your AMI or SaaS or Container product restricted](./resources/changeSets/products/ami/RestrictExistingAmi.json)|
|capi-18|[Update name and description of my public offer](./resources/changeSets/offers/UpdateEula.json)|
|capi-18|[Update EULA of my public offer](./resources/changeSets/offers/UpdateOfferNameAndDescription.json)|
|capi-18|[Update refund policy of my public offer](./resources/changeSets/offers/UpdateRefundPolicy.json)|
|capi-19|[Update geo-targeting of my public offer to specifically target few countries (e.g US/Canada/Spain) so that only customers in that region can subscribe to my offer](./resources/changeSets/offers/UpdateOfferTargeting.json)|
|capi-20|[Update price of my public offer for my AMI product with hourly annual pricing](./resources/changeSets/offers/UpdateOfferWithHourlyAnnualPricing.json)|
|capi-21|[Update price of my public offer for my SaaS product with contract and PAYG pricing](./resources/changeSets/offers/UpdateOfferWithContractAndPayAsYouGoPricing.json)|
|capi-23|[Add a new dimension to an AMI product and set the hourly price for this new dimension in the public offer](./resources/changeSets/products/ami/AddDimensionToAmiProductAndSetPriceInPublicOffer.json)|
|capi-24|[Update (e.g name) dimensions on my AMI or SaaS product](./resources/changeSets/products/saas/UpdateNameDimensionSaasProduct.json)|
|capi-25a|[Add a region where my AMI product is deployed](./resources/changeSets/products/ami/AddRegionExistingAmiProduct.json)|
|capi-25b|[Restrict a region where my AMI product is deployed](./resources/changeSets/products/ami/RestrictRegionExistingAmiProduct.json)|
|capi-26|[Specify if I want my AMI assets to be deployed in new regions built by AWS (future region support)](./resources/changeSets/products/ami/UpdateFutureRegionSupport.json)|
|capi-27|[List all my AMI or SaaS or Container products and associated public offers](./src/main/java/com/example/awsmarketplace/catalogapi/ListEntities.java)|
|capi-28|[Describe my AMI or SaaS or Container product and check if it contains all the information I need to know about the product](./src/main/java/com/example/awsmarketplace/catalogapi/DescribeEntity.java)|
|capi-29|[Describe my public offer and check if it contains all the information I need to know about the offer](./src/main/java/com/example/awsmarketplace/catalogapi/DescribeEntity.java)|
|capi-30|[Create draft private offers for my AMI or SaaS product so I can review them internally before publishing to my buyers](./resources/changeSets/offers/CreateDraftPrivateOffer.json)|
|capi-31|[Create a private offer with hourly annual pricing for my AMI product and add a custom EULA](./resources/changeSets/offers/CreatePrivateOfferWithHourlyAnnualPricingForAmiProduct.json)|
|capi-32|[Create a private offer with hourly pricing for my AMI product](./resources/changeSets/offers/CreatePrivateOfferWithHourlyPricingForAmi.json)|
|capi-35|[Create a private offer with contract pricing for my AMI product](./resources/changeSets/offers/CreatePrivateOfferWithContractPricingForAmiProduct.json)|
|capi-36|[Create a private offer (target buyers)for my Container product with contract pricing](./resources/changeSets/offers/CreatePrivateOfferWithContractPricingForContainerProduct.json)|
|capi-40|[List all my private offers and sort or filter them by Offer Publish Date, Offer Expiry Date and Buyer IDs](./src/main/java/com/example/awsmarketplace/catalogapi/ListAllPrivateOffers.java)|
|capi-41|[Create draft resale authorization for any product type (AMI/SaaS/Container) so I can review them internally before publishing to my CPs](./resources/changeSets/resaleAuthorization/DraftResaleauthAllProductType.json)|
|capi-42|[Publish a one-time resale authorization on my SaaS product so my CP can use that to create Channel Partner Private Offer (CPPO)](./resources/changeSets/resaleAuthorization/OnetimeResaleauthPrivateoffer.json)|
|capi-46|[Publish one-time resale authorization for any product type (AMI/SaaS/Container) and add a custom EULA to be sent to the buyer](./resources/changeSets/resaleAuthorization/OnetimeResaleauthCustomEula.json)|
|capi-47|[Publish one-time resale authorization for any product type (AMI/SaaS/Container) and add reseller contract documentation between the ISV and CP](./resources/changeSets/resaleAuthorization/OnetimeResaleauthCustomresellerContractdoc.json)|
|capi-48|[Publish multi-use resale authorization with expiry date for my AMI product with hourly annual pricing so my CP can use that to create CPPO](./resources/changeSets/resaleAuthorization/MultiuseResaleauthExpirydateCPPO.json)|
|capi-52|[Publish multi-use resale authorization without expiry date for my AMI product with hourly annual pricing so my CP can use that to create CPPO](./resources/changeSets/resaleAuthorization/MultiuseResaleautoNoExpirydateCPPO.json)|
|capi-56|[Publish multi-use resale authorization with expiry date for any product type (AMI/SaaS/Container) and add a custom EULA to be sent to the buyer](./resources/changeSets/resaleAuthorization/MultiuseResaleauthExpirydateCustomEula.json)|
|capi-57|[Publish multi-use resale authorization with expiry date for any product type (AMI/SaaS/Container) and add reseller contract documentation between the ISV and CP](./resources/changeSets/resaleAuthorization/MultiuseResaleauthExpirydateCustomresellerContractdoc.json)|
|capi-58|[Publish multi-use resale authorization without expiry date for any product type (AMI/SaaS/Container) and add a custom EULA to be sent to the buyer](./resources/changeSets/resaleAuthorization/MultiuseResaleauthNoExpirdateCustomEula.json)|
|capi-59|[Publish multi-use resale authorization without expiry date for any product type (AMI/SaaS/Container) and add reseller contract documentation between the ISV and CP](./resources/changeSets/resaleAuthorization/MultiuseResaleauthNoExpirydateCustomResellerContractdoc.json)|
|capi-60|[Create draft CPPO for any product type (AMI/SaaS/Container) so I can review them internally before publishing to my buyers](./resources/changeSets/channel_partner_offers/CreateDraftCppoOffer.json)|
|capi-63|[Publish CPPO using one-time resale authorization on AMI, SaaS, or Container products and update price markup](./resources/changeSets/channel_partner_offers/PublishCppoPiceMarkupObject.json)|
|capi-64|[Publish CPPO using one-time resale authorization on any product type (AMI/SaaS/Container) and append buyer EULA with what was received from ISV](./resources/changeSets/channel_partner_offers/PublishCppoEula.json)|
|capi-67|[Update the offer expiry date of a CPPO I created to a date in future so my buyers get more time to evaluate and accept the offer](./resources/changeSets/channel_partner_offers/UpdateCppoExpiryDate.json)|
|capi-68|[Publish CPPO using multi-use resale authorization with expiry date on AMI products and update price markup](./resources/changeSets/channel_partner_offers/PublishCppoPiceMarkupObject.json)|
|capi-69|[Publish CPPO using multi-use resale authorization with expiry date on SaaS products and update price markup](./resources/changeSets/channel_partner_offers/PublishCppoPiceMarkupObject.json)|
|capi-70|[Publish CPPO using multi-use resale authorization with expiry date on Container products and update price markup](./resources/changeSets/channel_partner_offers/PublishCppoPiceMarkupObject.json)|
|capi-71|[Publish CPPO using multi-use resale authorization with expiry date on any product type (AMI/SaaS/Container) and append buyer EULA with what was received from ISV](./resources/changeSets/channel_partner_offers/PublishCppoEula.json)|
|capi-72|[Publish more than one CPPO using multi-use resale authorization with or without expiry date on any product type (AMI/SaaS/Container) and update price markup](./resources/changeSets/channel_partner_offers/PublishCppoPiceMarkupObject.json)|
|capi-73|[Publish CPPO using multi-use resale authorization without expiry date on AMI products and update price markup](./resources/changeSets/channel_partner_offers/PublishCppoPiceMarkupObject.json)|
|capi-74|[Publish CPPO using multi-use resale authorization without expiry date on SaaS products and update price markup](./resources/changeSets/channel_partner_offers/PublishCppoPiceMarkupObject.json)|
|capi-75|[Publish CPPO using multi-use resale authorization without expiry date on Container products and update price markup](./resources/changeSets/channel_partner_offers/PublishCppoPiceMarkupObject.json)|
|capi-76|[Publish CPPO using multi-use resale authorization without expiry date on any product type (AMI/SaaS/Container) and append buyer EULA with what was received from ISV](./resources/changeSets/channel_partner_offers/PublishCppoEula.json)|
|capi-77|[Update name/description of one-time or multi-use resale authorization before publishing for any product type (AMI/SaaS/Container)](./resources/changeSets/resaleAuthorization/UpdateUnpublishedResaleAuthorization.json)|
|capi-78|[Publish one-time resale authorization for any product type (AMI/SaaS/Container) and add Flexible payment schedule](./resources/changeSets/resaleAuthorization/PublishOnetimeResaleAuthFlexiblePayment.json)|
|capi-81|[Publish one-time resale authorization for any product type (AMI/SaaS/Container) and add specific buyer account for the resale](./resources/changeSets/resaleAuthorization/PublishOnetimeResaleAuthSpecificBuyer.json)|
|capi-82|[Publish multi-use resale authorization with expiry date for any product type (AMI/SaaS/Container) and add specific buyer account for the resale](./resources/changeSets/resaleAuthorization/PublishMultiuseResaleAuthExpirydateSpecificBuyer.json)|
|capi-83|[Publish multi-use resale authorization without expiry date for any product type (AMI/SaaS/Container) and add specific buyer account for the resale](./resources/changeSets/resaleAuthorization/PublishMultiuseResaleAuthNoExpirydateSpecificBuyer.json)|
|capi-84|[Restrict a one-time resale authorization for any product type (AMI/SaaS/Container)](./resources/changeSets/resaleAuthorization/RestrictResaleAuthorization.json)|
|capi-90|[Publish one-time resale authorization for any product type (AMI/SaaS/Container) and add whether it is renewal or not](./resources/changeSets/resaleAuthorization/OnetimeResaleauthRenewal.json)|
|capi-91|[Create a custom dimension for an existing SaaS product and create a private offer](./resources/changeSets/offers/CreateSaasProductCustomDimensionAndPrivateOffer.json)|
|capi-92|[Describe a resale authorization](./src/main/java/com/example/awsmarketplace/catalogapi/DescribeEntity.java)|
|capi-93|[List all CPPOs created by a channel partner](./src/main/java/com/example/awsmarketplace/catalogapi/ListAllCppoOffers.java)|
|capi-94|[List all shared resale authorizations available to a channel partner](./src/main/java/com/example/awsmarketplace/catalogapi/ListAllSharedResaleAuthorizations.java)|
|capi-95|[Create a replacement private offer from an existing agreement with contract pricing](./resources/changeSets/offers/CreateReplacementPrivateOfferWithContractPricing.json)|
|capi-96|[Create a resale authorization replacement private offer from an existing agreement with contract pricing](./resources/changeSets/channel_partner_offers/CreateResaleAuthorizationReplacementOffer.json)|
|capi-97|[List and describe all private Offers associated with a product](./src/main/java/com/example/awsmarketplace/catalogapi/ListProductPrivateOffers.java)|
|capi-98|[List released Public/Private offers for a specific product id](./src/main/java/com/example/awsmarketplace/catalogapi/ListProductPublicOrPrivateReleasedOffers.java)|

## Agreement API reference code
|Id|Use case|
|-------|--------|
|ag-01|[Obtain a list of all of my agreements](./src/main/java/com/example/awsmarketplace/agreementapi/GetAllAgreements.java)|
|ag-02|[Filter my agreements based on product ID, Customer AWS Account ID, Offer ID](./src/main/java/com/example/awsmarketplace/agreementapi/SearchAgreementsByOneFilter.java)|
|ag-02-1|[Filter my agreements based on product ID](./src/main/java/com/example/awsmarketplace/agreementapi/SearchAgreementsByOneFilter.java)|
|ag-02-2|[Filter my agreements based on AWS Account ID](./src/main/java/com/example/awsmarketplace/agreementapi/SearchAgreementsByOneFilter.java)|
|ag-02-3|[Filter my agreements based on Offer ID](./src/main/java/com/example/awsmarketplace/agreementapi/SearchAgreementsByOneFilter.java)|
|ag-03|[Filter my agreements based on whether its end date is before or after a date I can specify (such as today)](./src/main/java/com/example/awsmarketplace/agreementapi/SearchAgreementsByEndDate.java)|
|ag-04|[Filter my agreements based on status](./src/main/java/com/example/awsmarketplace/agreementapi/SearchAgreementsByOneFilter.java)|
|ag-05|[Filter my agreement based on its product type ](./src/main/java/com/example/awsmarketplace/agreementapi/SearchAgreementsByOneFilter.java)|
|ag-06|[Filter my agreement based on a combination of any of the above filters ](./src/main/java/com/example/awsmarketplace/agreementapi/SearchAgreementsByTwoFilters.java)|
|ag-07|[Obtain metadata about my agreement, like its sign date, start date or end date](./src/main/java/com/example/awsmarketplace/agreementapi/DescribeAgreement.java)|
|ag-08|[Obtain metadata about the customer who created the agreement, such as the customer's AWS Account ID](./src/main/java/com/example/awsmarketplace/agreementapi/GetAgreementCustomerInfo.java)|
|ag-09|[Obtain all the Agreement IDs](./src/main/java/com/example/awsmarketplace/agreementapi/GetAllAgreementsIds.java)|
|ag-10|[Obtain information about the product and offer that the agreement was created on such as Product ID and Offer ID](./src/main/java/com/example/awsmarketplace/agreementapi/GetProductAndOfferDetailFromAgreement.java)|
|ag-11|[Obtain the Product Type of the product the agreement was created on ](./src/main/java/com/example/awsmarketplace/agreementapi/GetAgreementProductType.java)|
|ag-13|[Retrieve the status of the agreement](./src/main/java/com/example/awsmarketplace/agreementapi/GetAgreementStatus.java)|
|ag-14|[Obtain financial details, such as Total Contract Value of the agreement](./src/main/java/com/example/awsmarketplace/agreementapi/GetAgreementFinancialDetails.java)|
|ag-15|[Obtain the auto-renewal status of the agreement ](./src/main/java/com/example/awsmarketplace/agreementapi/GetAgreementAutoRenewal.java)|
|ag-16|[Obtain the pricing type of the agreement (contract, FPS, metered, free etc.)](./src/main/java/com/example/awsmarketplace/agreementapi/GetAgreementPricingType.java)|
|ag-17|[Obtain the payment schedule I have agreed to with the agreement, including the invoice date and invoice amount](./src/main/java/com/example/awsmarketplace/agreementapi/GetAgreementTermsPaymentSchedule.java)|
|ag-18|[Obtain the EULA I have entered into with my customer via the agreement](./src/main/java/com/example/awsmarketplace/agreementapi/GetAgreementTermsEula.java)|
|ag-19|[Obtain the support and refund policy I have provided to the customer](./src/main/java/com/example/awsmarketplace/agreementapi/GetAgreementTermsSupportTerm.java)|
|ag-20|[Obtain the details from an agreement of a free trial I have provided to the customer](./src/main/java/com/example/awsmarketplace/agreementapi/GetAgreementTermsFreeTrialDetails.java)|
|ag-28|[Obtain the dimensions the buyer has purchased from me via the agreement](./src/main/java/com/example/awsmarketplace/agreementapi/GetAgreementTermsDimensionPurchased.java)|
|ag-29|[Obtain pricing per each dimension in the agreement](./src/main/java/com/example/awsmarketplace/agreementapi/GetAgreementTermsPricingEachDimension.java)|
|ag-30|[Obtain instances of each dimension that buyer has purchased in the agreement](./src/main/java/com/example/awsmarketplace/agreementapi/GetAgreementTermsDimensionInstances.java)|

### Submit defects & questions
If you find any defects with the APIs, need help troubleshooting, or have general questions or feedback, [use this form to contact us](https://aws.amazon.com/marketplace/management/contact-us/)


## AWS SDK for Java

Get started quickly using AWS in java, the AWS SDK for Java makes it easy to integrate your Java application, library, or script with AWS services including Amazon S3, Amazon EC2, Amazon DynamoDB, and more.

https://aws.amazon.com/sdk-for-java/

## AWS Marketplace Documentation

To access detailed AWS Marketplace API documentation:

https://docs.aws.amazon.com/marketplace/

