"""
Purpose
Shows how to use the AWS SDK for Python (Boto3) to describe a resale authorization
in an account

Program executed with single argument:
ie. python3 describe_resale_authorization.py --entity-id <entity_id>

CAPI-92
"""

import argparse
import logging

import boto3
import utils.helpers as hlp  # noqa: E402
from botocore.exceptions import ClientError

mp_client = boto3.client("marketplace-catalog")


def get_entity(entity_id):
    try:
        response = mp_client.describe_entity(
            Catalog="AWSMarketplace", EntityId=entity_id
        )
    except ClientError as e:
        logging.exception(f"Couldn't get the entity. {e}")
        raise

    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--entity-id",
        "-e",
        help="Entity ID of the resale authorization to describe",
        required=True,
    )
    args = parser.parse_args()

    response = get_entity(entity_id=args.entity_id)

    hlp.pretty_print_datetime(response)
