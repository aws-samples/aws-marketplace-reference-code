"""
Purpose
Shows how to use the AWS SDK for Python (Boto3) to set expiry date of a private offer to a date in the past so that my buyers no longer see the offer.
CAPI-38
"""

import os

import utils.start_changeset as sc
import utils.stringify_details as sd

fname = "changeset.json"
change_set_file = os.path.join(os.path.dirname(__file__), fname)

change_set = sd.stringify_changeset(change_set_file)


def main():
    sc.usage_demo(change_set, "Expire a private offer")


if __name__ == "__main__":
    main()
