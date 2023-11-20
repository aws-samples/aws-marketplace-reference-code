"""
Purpose
Publish multi-use resale authorization with expiry date for any product type (AMI/SaaS/Container) and add specific buyer account for the resale
CAPI-82
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
        "Publish multi-use resale authorization with expiry date for any product type (AMI/SaaS/Container) and add specific buyer account for the resale",
    )


if __name__ == "__main__":
    main()
