"""
Purpose
Shows how to use the AWS SDK for Python (Boto3) to publish “draft” CPPO
for any product type (AMI/SaaS/Container) and update price markup
CAPI-72
"""

import json
import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# For multiple cppo;
numbOfCPPOs = 1

resaleAuthorizationId = "resaleauthz-1111111111111"

priceMarkupPer = "5.0"

buyerAccount = "111111111111"

availabilityEndDate = "2023-06-30"

agreementDuration = "P450D"

details_create_offer_object = {
    "ResaleAuthorizationId": resaleAuthorizationId
}

details_create_offer_string = json.dumps(details_create_offer_object)

details_information_object = {
    "Name": "Test Offer name",
    "Description": "Test Offer description"
}

details_information_string = json.dumps(details_information_object)

details_price_object = {"Percentage": priceMarkupPer}

details_price_string = json.dumps(details_price_object)

details_targeting_object = {"PositiveTargeting": {"BuyerAccounts": [buyerAccount]}}

details_targeting_string = json.dumps(details_targeting_object)

details_availability_object = {"AvailabilityEndDate": availabilityEndDate}

details_availability_string = json.dumps(details_availability_object)

details_validityTerms_object = {
    "Terms": [{"Type": "ValidityTerm", "AgreementDuration": agreementDuration}]
}

details_validityTerms_string = json.dumps(details_validityTerms_object)


def publish_cppo_price_markup(mp_client):
    """
    update price markup AND publish offer
    """
    try:
        response = mp_client.start_change_set(
            Catalog="AWSMarketplace",
            ChangeSet=[
                {
                    "ChangeType": "CreateOfferUsingResaleAuthorization",
                    "Entity": {"Type": "Offer@1.0"},
                    "ChangeName": "CreateCPPO",
                    "Details": details_create_offer_string,
                },
                {
                    "ChangeType": "UpdateInformation",
                    "Entity": {
                        "Type": "Offer@1.0",
                        "Identifier": "$CreateCPPO.Entity.Identifier",
                    },
                    "Details": details_information_string,
                },                
                {
                    "ChangeType": "UpdateMarkup",
                    "Entity": {
                        "Type": "Offer@1.0",
                        "Identifier": "$CreateCPPO.Entity.Identifier",
                    },
                    "Details": details_price_string,
                },
                {
                    "ChangeType": "UpdateTargeting",
                    "Entity": {
                        "Type": "Offer@1.0",
                        "Identifier": "$CreateCPPO.Entity.Identifier",
                    },
                    "Details": details_targeting_string,
                },
                {
                    "ChangeType": "UpdateAvailability",
                    "Entity": {
                        "Type": "Offer@1.0",
                        "Identifier": "$CreateCPPO.Entity.Identifier",
                    },
                    "Details": details_availability_string,
                },
                {
                    "ChangeType": "UpdateValidityTerms",
                    "Entity": {
                        "Type": "Offer@1.0",
                        "Identifier": "$CreateCPPO.Entity.Identifier",
                    },
                    "Details": details_validityTerms_string,
                },
                {
                    "ChangeType": "ReleaseOffer",
                    "Entity": {
                        "Type": "Offer@1.0",
                        "Identifier": "$CreateCPPO.Entity.Identifier",
                    },
                    "Details": "{}",
                },
            ],
            ChangeSetName="Publish CPPO offer using resale authorization update price markup",
        )
        logger.info("Changeset created!")
        logger.info(f"ChangeSet ID: {response['ChangeSetId']}")
        logger.info(f"ChangeSet ARN: {response['ChangeSetArn']}")

    except ClientError as e:
        logger.exception(f"Couldn't create offer. {e}")
        raise


def usage_demo():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    print("-" * 88)
    print(
        "Welcome to the publish CPPO draft offer using resale authorization and update price markup."
    )
    print("-" * 88)

    mp_client = boto3.client("marketplace-catalog")
    for _ in range(numbOfCPPOs):
        publish_cppo_price_markup(mp_client)

    print("-" * 88)


if __name__ == "__main__":
    usage_demo()