import utils.start_changeset as sc
import utils.stringify_details as sd
import tests.helpers as test_helpers

import src.catalog_api.products.ami.create_draft_ami_product_with_draft_public_offer.start_changeset as capi_02
import src.catalog_api.products.ami.create_limited_ami_product_and_public_offer_with_hourly_annual_pricing.start_changeset as capi_06
import src.catalog_api.products.ami.create_limited_ami_product_and_public_offer_with_hourly_pricing.start_changeset as capi_07
import src.catalog_api.products.ami.add_region_existing_ami_product.start_changeset as capi_25a
import src.catalog_api.products.ami.restrict_region_existing_ami_product.start_changeset as capi_25b


# this test needs to be run in primary seller account
def test_capi_02():
    unpatched_changeset_json = sd.open_json_file(
        "src/catalog_api/products/ami/create_draft_ami_product_with_draft_public_offer/changeset.json"
    )

    changeset_stringified = sd.stringify_details_sections(unpatched_changeset_json)

    response = capi_02.main(
        changeset_stringified,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


# this test needs to be run in primary seller account
def test_capi_06():
    unpatched_changeset_json = sd.open_json_file(
        "src/catalog_api/products/ami/create_limited_ami_product_and_public_offer_with_hourly_annual_pricing/changeset.json"
    )

    patched_changeset_json = test_helpers.patch_json_params(
        unpatched_changeset_json, "/capi-06"
    )
    changeset_stringified = sd.stringify_details_sections(patched_changeset_json)

    response = capi_06.main(
        changeset_stringified,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


# this test needs to be run in primary seller account
def test_capi_07():
    unpatched_changeset_json = sd.open_json_file(
        "src/catalog_api/products/ami/create_limited_ami_product_and_public_offer_with_hourly_pricing/changeset.json"
    )

    patched_changeset_json = test_helpers.patch_json_params(
        unpatched_changeset_json, "/capi-07"
    )
    changeset_stringified = sd.stringify_details_sections(patched_changeset_json)

    response = capi_07.main(
        changeset_stringified,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


# this test needs to be run in primary seller account
def test_capi_25a():
    unpatched_changeset_json = sd.open_json_file(
        "src/catalog_api/products/ami/add_region_existing_ami_product/changeset.json"
    )

    patched_changeset_json = test_helpers.patch_json_params(
        unpatched_changeset_json, "/capi-25a"
    )
    changeset_stringified = sd.stringify_details_sections(patched_changeset_json)

    response = capi_25a.main(
        changeset_stringified,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


# this test needs to be run in primary seller account
def test_capi_25b():
    unpatched_changeset_json = sd.open_json_file(
        "src/catalog_api/products/ami/restrict_region_existing_ami_product/changeset.json"
    )

    patched_changeset_json = test_helpers.patch_json_params(
        unpatched_changeset_json, "/capi-25b"
    )
    changeset_stringified = sd.stringify_details_sections(patched_changeset_json)

    response = capi_25b.main(
        changeset_stringified,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
