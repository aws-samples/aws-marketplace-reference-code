import boto3
from botocore.exceptions import ClientError

import logging

logger = logging.getLogger(__name__)

ssm_client = boto3.client("ssm")


def get_parameter(parameter_name):
    """
    This function will retrieve the value from parameter store for a
    given parameter.  Used by test cases to provide arguments to use cases
    """

    try:
        response = ssm_client.get_parameter(Name=parameter_name)
    except ClientError as e:
        logger.exception(f"Couldn't get parameter. {e}")
        raise

    return response["Parameter"]["Value"]
