import utils.start_changeset as sc
import utils.stringify_details as sd
import tests.helpers as test_helpers

import src.catalog_api.products.container.create_draft_container_product_with_draft_public_offer.start_changeset as capi_03
import src.catalog_api.products.container.create_limited_container_product_public_offer.start_changeset as capi_15


# this test needs to be run in primary seller account
def test_capi_03():
    unpatched_changeset_json = sd.open_json_file(
        "src/catalog_api/products/container/create_draft_container_product_with_draft_public_offer/changeset.json"
    )

    changeset_stringified = sd.stringify_details_sections(unpatched_changeset_json)

    response = capi_03.main(
        changeset_stringified,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


# this test needs to be run in primary seller account
def test_capi_15():
    unpatched_changeset_json = sd.open_json_file(
        "src/catalog_api/products/container/create_limited_container_product_public_offer/changeset.json"
    )

    patched_changeset_json = test_helpers.patch_json_params(
        unpatched_changeset_json, "/capi-15"
    )
    changeset_stringified = sd.stringify_details_sections(patched_changeset_json)

    response = capi_15.main(
        changeset_stringified,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
