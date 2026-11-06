# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Purpose
Shows how to use the AWS SDK for Python (Boto3) to replace the standalone free trial offer of my SaaS product
with a free trial that converts to paid usage on the public offer. The change set sets the expiry date of the
standalone free trial offer (offer-2222222222222) to a date in the past so that my buyers no longer see that offer,
and adds the free trial to the public usage offer (offer-1111111111111).
CAPI-114
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
        "Enable free trial auto-conversion for a SaaS product",
    )

    return response


if __name__ == "__main__":
    main()
