"""
Purpose
Update name/description of one-time or multi-use resale authorization before publishing for any product type (AMI/SaaS/Container)
CAPI-77
"""

import os

import utils.start_changeset as sc
import utils.stringify_details as sd

fname = "changeset.json"
change_set_file = os.path.join(os.path.dirname(__file__), fname)

change_set = sd.stringify_changeset(change_set_file)


def main():
    sc.usage_demo(
        change_set,
        "update name and description of one-time or multi-use resale authorization before publishing for any product type",
    )


if __name__ == "__main__":
    main()
