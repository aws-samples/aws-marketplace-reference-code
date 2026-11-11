# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Purpose
Shows how to use the AWS SDK for Python (Boto3) to add a free trial that converts to a paid subscription
to the public offer of my SaaS subscription product.
UpdatePricingTerms replaces all pricing terms, so copy your offer's current UsageBasedPricingTerm from
DescribeEntity instead of using the example rates, and grant every dimension in the free trial.
CAPI-113
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
        "Add a free trial that converts to a paid subscription to the public offer of a SaaS subscription product",
    )

    return response


if __name__ == "__main__":
    main()
