"""
Purpose
Shows how to use the AWS SDK for Python (Boto3) to publish CPPO
for any product type (AMI/SaaS/Container) and append buyer EULA
"""

import json
import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

resaleAuthorizationId = "resaleauthz-1111111111111"

legalTermUrl = "https://aws-mp-standard-contracts.s3.amazonaws.com/Standard-Contact-for-AWS-Marketplace-2022-07-14.pdf"

buyerAccount = "111111111111"

availabilityEndDate = "2023-05-31"

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

details_legalTerm_object = {
    "Terms": [
        {
            "Type": "LegalTerm",
            "Documents": [{"Type": "CustomEula", "Url": legalTermUrl}],
        }
    ]
}

details_legalTerm_string = json.dumps(details_legalTerm_object)

details_targeting_object = {"PositiveTargeting": {"BuyerAccounts": [buyerAccount]}}

details_targeting_string = json.dumps(details_targeting_object)

details_availability_object = {"AvailabilityEndDate": availabilityEndDate}

details_availability_string = json.dumps(details_availability_object)

details_validityTerms_object = {
    "Terms": [{"Type": "ValidityTerm", "AgreementDuration": agreementDuration}]
}

details_validityTerms_string = json.dumps(details_validityTerms_object)


def publish_cppo_eula(mp_client):
    """
    {Publish CPPO and append EULA}
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
                    "ChangeType": "UpdateLegalTerms",
                    "Entity": {
                        "Type": "Offer@1.0",
                        "Identifier": "$CreateCPPO.Entity.Identifier",
                    },
                    "Details": details_legalTerm_string,
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
            ChangeSetName="Publish CPPO offer using resale authorization and append buyer EULA",
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
        "Welcome to the publish CPPO draft offer using resale authorization and append EULA."
    )
    print("-" * 88)

    mp_client = boto3.client("marketplace-catalog")

    publish_cppo_eula(mp_client)

    print("-" * 88)


if __name__ == "__main__":
    usage_demo()