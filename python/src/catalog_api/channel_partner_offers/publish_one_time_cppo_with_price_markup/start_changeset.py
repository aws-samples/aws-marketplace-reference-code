"""
Purpose
Shows how to use the AWS SDK for Python (Boto3) to Create CPPO using one-time resale
authorization on AMI, SaaS or Container products and update price markup
CAPI-63
"""


import os

import utils.start_changeset as sc
import utils.stringify_details as sd


def main(change_set=None):
    if change_set is None:
        fname = "changeset.json"
        change_set_file = os.path.join(os.path.dirname(__file__), fname)
        stringified_change_set = sd.stringify_changeset(change_set_file)

    else:
        stringified_change_set = change_set

    response = sc.usage_demo(
        stringified_change_set,
        "Create CPPO using one-time resale authorization and update price markup"
    )

    return response


if __name__ == "__main__":
    main()
