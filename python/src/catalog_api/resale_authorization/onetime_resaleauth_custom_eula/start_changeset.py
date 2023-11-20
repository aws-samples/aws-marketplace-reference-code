"""
Purpose
Publish a one-time resale authorization on my SaaS/AMI/Container product and add custom EULA to be sent to the buyer
"""

import os

import utils.start_changeset as sc
import utils.stringify_details as sd

fname = "changeset.json"
change_set_file = os.path.join(os.path.dirname(__file__), fname)

change_set = sd.stringify_changeset(change_set_file)


def main():
    sc.usage_demo(change_set, "onetime resale auth with custom EULA")


if __name__ == "__main__":
    main()
