from .get_args import get_parameter

import src.catalog_api.products.saas.create_draft_saas_product_with_draft_public_offer.start_changeset as capi_04


def test_capi_04():
    response = capi_04.main()

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
