import utils.start_changeset as sc
import utils.stringify_details as sd
import tests.helpers as test_helpers

from .get_args import get_parameter

import src.catalog_api.resale_authorization.multiuse_resaleauth_expirydate_customreseller_contractdoc.start_changeset as capi_57


def test_capi_57():
    unpatched_changeset_json = sd.open_json_file(
        "src/catalog_api/resale_authorization/multiuse_resaleauth_expirydate_customreseller_contractdoc/changeset.json"
    )

    patched_changeset_json = test_helpers.patch_json_params(
        unpatched_changeset_json, "/capi-57"
    )
    changeset_stringified = sd.stringify_details_sections(patched_changeset_json)

    response = capi_57.main(
        changeset_stringified,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
