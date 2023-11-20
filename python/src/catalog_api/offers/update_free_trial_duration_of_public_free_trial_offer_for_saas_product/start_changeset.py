"""
Purpose
Shows how to use the AWS SDK for Python (Boto3) to change free trial duration for my SaaS product by modifying my free trial public offer
CAPI-14
"""

import os

import utils.start_changeset as sc
import utils.stringify_details as sd

fname = "changeset.json"
change_set_file = os.path.join(os.path.dirname(__file__), fname)

change_set = sd.stringify_changeset(change_set_file)


def main():
    sc.usage_demo(change_set, "Change free trial duration for SaaS product")


if __name__ == "__main__":
    main()
