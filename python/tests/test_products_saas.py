import utils.start_changeset as sc
import utils.stringify_details as sd
import tests.helpers as test_helpers

import src.catalog_api.products.saas.create_draft_saas_product_with_draft_public_offer.start_changeset as capi_04
import src.catalog_api.products.saas.publish_saas_product_public_offer.start_changeset1 as capi_05a1
import src.catalog_api.products.saas.publish_saas_product_public_offer.start_changeset2 as capi_05a2
import src.catalog_api.products.saas.update_name_dimension_saas_product.start_changeset as capi_24


# this test needs to be run in primary seller account
def test_capi_04():
    unpatched_changeset_json = sd.open_json_file(
        "src/catalog_api/products/saas/create_draft_saas_product_with_draft_public_offer/changeset.json"
    )

    changeset_stringified = sd.stringify_details_sections(unpatched_changeset_json)

    response = capi_04.main(
        changeset_stringified,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


# this test needs to be run in primary seller account
def test_capi_05a_v1():
    unpatched_changeset_json = sd.open_json_file(
        "src/catalog_api/products/saas/publish_saas_product_public_offer/changeset1.json"
    )

    patched_changeset_json = test_helpers.patch_json_params(
        unpatched_changeset_json, "/capi-05a-1"
    )
    changeset_stringified = sd.stringify_details_sections(patched_changeset_json)

    response = capi_05a1.main(
        changeset_stringified,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


# this test needs to be run in primary seller account
def test_capi_05a_v2():
    unpatched_changeset_json = sd.open_json_file(
        "src/catalog_api/products/saas/publish_saas_product_public_offer/changeset2.json"
    )

    patched_changeset_json = test_helpers.patch_json_params(
        unpatched_changeset_json, "/capi-05a-2"
    )
    changeset_stringified = sd.stringify_details_sections(patched_changeset_json)

    response = capi_05a2.main(
        changeset_stringified,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


# this test needs to be run in primary seller account
def test_capi_24():
    unpatched_changeset_json = sd.open_json_file(
        "src/catalog_api/products/saas/update_name_dimension_saas_product/changeset.json"
    )

    patched_changeset_json = test_helpers.patch_json_params(
        unpatched_changeset_json, "/capi-24"
    )
    changeset_stringified = sd.stringify_details_sections(patched_changeset_json)

    response = capi_24.main(
        changeset_stringified,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
