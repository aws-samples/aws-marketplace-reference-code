from .get_args import get_parameter

import src.catalog_api.channel_partner_offers.describe_resale_authorization.describe_resale_authorization as capi_92
import src.catalog_api.channel_partner_offers.list_all_cppo_offers.list_all_cppo_offers as capi_93
import src.catalog_api.channel_partner_offers.list_all_shared_resale_authorizations.list_all_shared_resale_authorizations as capi_94


def test_capi_92():
    entity_id = get_parameter("/marketplacesamples/capi-92/resaleauthorizationid")

    response = capi_92.get_entity(entity_id)

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_capi_93():
    response = capi_93.get_resaleauth_offers()

    assert type(response) == list


def test_capi_94():
    response = capi_94.get_shared_entities()

    assert type(response) == list
