"""
Purpose
Shows how to use the AWS SDK for Python (Boto3) to get product and offer details in a given agreement
AG-10
"""

import argparse
import logging

import boto3
import utils.helpers as helper
from botocore.exceptions import ClientError

mpa_client = boto3.client("marketplace-agreement")
mpc_client = boto3.client("marketplace-catalog")

logger = logging.getLogger(__name__)


def get_agreement_information(agreement_id):
    """
    Returns information about a given agreement
    Args: agreement_id str: Entity to return
    Returns: dict: Dictionary of agreement information
    """

    try:
        agreement = mpa_client.describe_agreement(agreementId=agreement_id)

        return agreement

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logger.error("Agreement with ID %s not found.", agreement_id)
        else:
            logger.error("Unexpected error: %s", e)


def get_entity_information(entity_id):
    """
    Returns information about a given entity
    Args: entity_id str: Entity to return
    Returns: dict: Dictionary of entity information
    """

    try:
        response = mpc_client.describe_entity(
            Catalog="AWSMarketplace",
            EntityId=entity_id,
        )

        return response

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            logger.error("Entity with ID %s not found.", entity_id)
        else:
            logger.error("Unexpected error: %s", e)


def get_agreement_components(agreement_id):
    agreement_component_list = []

    agreement = get_agreement_information(agreement_id)

    if agreement is not None:
        productIds = []
        for resource in agreement["proposalSummary"]["resources"]:
            productIds.append(resource["id"])

        for product_id in productIds:
            product_document = get_entity_information(product_id)

            product_document_dict = {}
            product_document_dict["product_id"] = product_id
            product_document_dict["document"] = product_document
            agreement_component_list.append(product_document_dict)

        offerId = agreement["proposalSummary"]["offerId"]

        offer_document = get_entity_information(offerId)

        offer_document_dict = {}
        offer_document_dict["offer_id"] = offerId
        offer_document_dict["document"] = offer_document
        agreement_component_list.append(offer_document_dict)

        return agreement_component_list

    else:
        print("Agreement with ID " + args.agreement_id + " is not found")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--agreement_id",
        "-aid",
        help="Provide agreement ID to search for product and offer detail",
        required=True,
    )
    args = parser.parse_args()

    product_offer_detail = get_agreement_components(agreement_id=args.agreement_id)

    helper.pretty_print_datetime(product_offer_detail)
