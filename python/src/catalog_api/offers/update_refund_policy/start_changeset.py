"""
Purpose
Shows how to use the AWS SDK for Python (Boto3) to update refund policy of my offer
CAPI-18
"""

import os

import utils.start_changeset as sc  # type: ignore
import utils.stringify_details as sd  # type: ignore

fname = "changeset.json"
change_set_file = os.path.join(os.path.dirname(__file__), fname)

change_set = sd.stringify_changeset(change_set_file)


def main():
    sc.usage_demo(change_set, "Update refund policy of my public offer")


if __name__ == "__main__":
    main()
