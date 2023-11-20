import jsonpatch
import json
import utils.start_changeset as sc
import utils.stringify_details as sd
import boto3
from botocore.exceptions import ClientError
import logging
import time
from datetime import datetime

curr_dt = datetime.now()

logger = logging.getLogger(__name__)

ssm_client = boto3.client("ssm")
mktplace_client = boto3.client("marketplace-catalog")


def pretty_print(json_obj):
    print(json.dumps(json_obj, indent=4, default=str))


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


def create_parameter(parameter_name, parameter_value):
    try:
        response = ssm_client.put_parameter(
            Name=parameter_name, Value=parameter_value, Type="String", Overwrite=True
        )
    except ClientError as e:
        logger.exception(f"Couldn't create parameter. {e}")
        raise

    return response


def describe_entity(entity_id):
    response = mktplace_client.describe_entity(
        Catalog="AWSMarketplace", EntityId=entity_id
    )

    return response


def describe_changeset(changeset_id):
    response = mktplace_client.describe_change_set(
        Catalog="AWSMarketplace", ChangeSetId=changeset_id
    )

    return response


def get_product_id(changeset_id):
    response = describe_changeset(changeset_id)

    # check if key is in response dictionary
    if response["Status"] == "APPLYING" or response["Status"] == "SUCCEEDED":
        print(f"Product ID is: {response['ChangeSet'][0]['Entity']['Identifier']}")

        product_id = response["ChangeSet"][0]["Entity"]["Identifier"]
        # if product_id ends with '@1' strip it from the end of the string
        if product_id.endswith("@1"):
            product_id = product_id[:-2]

        return product_id

    elif response["Status"] == "FAILED" or response["Status"] == "CANCELLED":
        print(
            f"No product ID will be available as changeset {changeset_id} failed or was cancelled."
        )
        return None

    elif response["Status"] == "PREPARING":
        print(f"Changeset: {changeset_id} STILL being prepared")

        return "PREPARING"


def poll_changeset_status(changeset_id):
    continue_polling = True

    while continue_polling:
        product_response = get_product_id(changeset_id)

        if product_response == "PREPARING":
            continue_polling = True
            time.sleep(3)

        else:
            continue_polling = False

    return product_response


def get_all_parameters(path):
    response = ssm_client.get_parameters_by_path(Path=path, Recursive=True)

    if response["Parameters"]:
        pretty_print(response["Parameters"])
        return response


def patch_json_params(json_obj, param_path):
    # get all parameters from parameter store
    parameters = get_all_parameters(param_path)

    # loop through parameters and patch json
    for param in parameters["Parameters"]:
        print(f"Parameter Name: {param['Name']}")
        print(f"Parameter Value: {param['Value']}")

        # monkey patch repo-name for uniqque string
        if (
            param["Name"]
            == "/capi-15/changeSet/4/DetailsDocument/Repositories/0/RepositoryName"
        ):
            # generate a timestamp to make container name unique
            param["Value"] = "containerrepo" + str(int(round(curr_dt.timestamp())))

        # get the json path from the parameter name
        json_path = param["Name"].split(param_path)[1]
        print(f"JSON Path: {json_path}")

        # patch the json with the parameter value
        json_obj = jsonpatch.apply_patch(
            json_obj, [{"op": "replace", "path": json_path, "value": param["Value"]}]
        )

    return json_obj
