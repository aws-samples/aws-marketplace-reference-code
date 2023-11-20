import utils.start_changeset as sc
import utils.stringify_details as sd
import tests.helpers as test_helpers

import src.catalog_api.resale_authorization.onetime_resaleauth_renewal.start_changeset as capi_90


# this test needs to be run in primary seller account
def test_capi_90():
    unpatched_changeset_json = sd.open_json_file(
        "src/catalog_api/resale_authorization/onetime_resaleauth_renewal/changeset.json"
    )

    patched_changeset_json = test_helpers.patch_json_params(
        unpatched_changeset_json, "/capi-90"
    )
    changeset_stringified = sd.stringify_details_sections(patched_changeset_json)

    response = capi_90.main(
        changeset_stringified,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
