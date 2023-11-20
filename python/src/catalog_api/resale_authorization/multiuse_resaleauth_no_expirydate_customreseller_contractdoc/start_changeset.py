"""
Purpose
Publish a multi-use resale authorization with no expiry date on my SaaS/AMI/Container product and add reseller contract documentation between the ISV and channel partner
CAPI-59
"""

import os

import utils.start_changeset as sc
import utils.stringify_details as sd

fname = "changeset.json"
change_set_file = os.path.join(os.path.dirname(__file__), fname)

change_set = sd.stringify_changeset(change_set_file)


def main():
    sc.usage_demo(
        change_set, "multi use resale auth with no expiry date and contract doc"
    )


if __name__ == "__main__":
    main()
