import utils.start_changeset as sc
import utils.stringify_details as sd
import tests.helpers as test_helpers

import src.catalog_api.offers.create_private_offer_with_contract_pricing_for_container_product.start_changeset as capi_36
import src.catalog_api.offers.create_private_offer_with_contract_pricing_with_flexible_payment_schedule_for_saas_product.start_changeset as capi_39
import src.catalog_api.offers.create_replacement_private_offer_with_contract_pricing.start_changeset as capi_95
import src.catalog_api.channel_partner_offers.create_resale_authorization_replacement_offer.start_changeset as capi_96


# this test needs to be run in primary seller account
def test_capi_36():
    unpatched_changeset_json = sd.open_json_file(
        "src/catalog_api/offers/create_private_offer_with_contract_pricing_for_container_product/changeset.json"
    )

    patched_changeset_json = test_helpers.patch_json_params(
        unpatched_changeset_json, "/capi-36"
    )
    changeset_stringified = sd.stringify_details_sections(patched_changeset_json)

    response = capi_36.main(
        changeset_stringified,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


# this test needs to be run in primary seller account
def test_capi_39():
    unpatched_changeset_json = sd.open_json_file(
        "src/catalog_api/offers/create_private_offer_with_contract_pricing_with_flexible_payment_schedule_for_saas_product/changeset.json"
    )

    patched_changeset_json = test_helpers.patch_json_params(
        unpatched_changeset_json, "/capi-39"
    )
    changeset_stringified = sd.stringify_details_sections(patched_changeset_json)

    response = capi_39.main(
        changeset_stringified,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


# this test needs to be run in primary seller account
def test_capi_95():
    unpatched_changeset_json = sd.open_json_file(
        "src/catalog_api/offers/create_replacement_private_offer_with_contract_pricing/changeset.json"
    )

    patched_changeset_json = test_helpers.patch_json_params(
        unpatched_changeset_json, "/capi-95"
    )
    changeset_stringified = sd.stringify_details_sections(patched_changeset_json)

    response = capi_95.main(
        changeset_stringified,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


# this test needs to be run in channel partner account
def test_capi_96():
    unpatched_changeset_json = sd.open_json_file(
        "src/catalog_api/channel_partner_offers/create_resale_authorization_replacement_offer/changeset.json"
    )

    patched_changeset_json = test_helpers.patch_json_params(
        unpatched_changeset_json, "/capi-96"
    )
    changeset_stringified = sd.stringify_details_sections(patched_changeset_json)

    response = capi_96.main(
        changeset_stringified,
    )

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
