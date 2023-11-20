"""
Purpose
Publish my SaaS product and associated public offer (product will be in limited state by default)
CAPI-05A
"""

import os

import utils.start_changeset as sc
import utils.stringify_details as sd


def main(change_set=None):
    if change_set is None:
        fname = "changeset1.json"
        change_set_file = os.path.join(os.path.dirname(__file__), fname)
        stringified_change_set = sd.stringify_changeset(change_set_file)

    else:
        stringified_change_set = change_set

    response = sc.usage_demo(
        stringified_change_set,
        "publish saas product and associated public offer",
    )

    return response


if __name__ == "__main__":
    main()
