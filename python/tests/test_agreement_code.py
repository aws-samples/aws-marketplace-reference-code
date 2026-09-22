import utils.start_changeset as sc
import utils.stringify_details as sd
import tests.helpers as test_helpers

import src.agreements_api.seller.get_all_agreements.get_all_agreements as ag_01
import src.agreements_api.seller.search_agreements_by_account_id.search_agreements_by_account_id as ag_02
import src.agreements_api.seller.search_agreements_by_endDate.search_agreements_by_endDate as ag_03
import src.agreements_api.seller.search_agreements_by_status.search_agreements_by_status as ag_04
import src.agreements_api.seller.describe_agreement.describe_agreement as ag_07
import src.agreements_api.seller.get_agreement_customer.get_agreement_customer as ag_08
import src.agreements_api.seller.get_all_agreement_ids.get_all_agreement_ids as ag_09
import src.agreements_api.seller.get_agreement_product_offer_detail.get_agreement_product_offer_detail as ag_10
import src.agreements_api.seller.get_agreement_status.get_agreement_status as ag_13
import src.agreements_api.seller.get_agreement_financial_details.get_agreement_financial_details as ag_14
import src.agreements_api.seller.get_agreement_auto_renewal.get_agreement_auto_renewal as ag_15
import src.agreements_api.seller.get_agreement_support_terms.get_agreement_support_terms as ag_19
import src.agreements_api.seller.get_agreement_free_trial_details.get_agreement_free_trial_details as ag_20
import src.agreements_api.seller.search_agreements_renewing.search_agreements_renewing as ag_31
import src.agreements_api.seller.get_agreement_end_time_behavior.get_agreement_end_time_behavior as ag_32
import src.agreements_api.seller.get_agreement_initial_agreement.get_agreement_initial_agreement as ag_33
import src.agreements_api.seller.search_agreements_by_startDate.search_agreements_by_startDate as ag_34
import src.agreements_api.seller.search_agreements_by_lastUpdateDate.search_agreements_by_lastUpdateDate as ag_35
import src.agreements_api.seller.search_agreements_acceptor_opted_out.search_agreements_acceptor_opted_out as ag_36


# this test needs to be run in primary seller account
def test_ag_01():
    party_type_list = ["Proposer"]
    agreement_type_list = ["PurchaseAgreement"]
    resource_type_list = ["SaaSProduct"]

    filter_list = [
        {"name": "PartyType", "values": party_type_list},
        {"name": "AgreementType", "values": agreement_type_list},
        {"name": "ResourceType", "values": resource_type_list},
    ]

    response = ag_01.get_agreements(filter_list)

    assert type(response) is list


def test_ag_02():
    agreement_id = test_helpers.get_parameter("/ag-07/agreement-id")

    response = ag_02.get_agreements(agreement_id)

    assert type(response) is list


def test_ag_03():
    response = ag_03.get_agreements()

    assert type(response) is list


def test_ag_04():
    response = ag_04.get_agreements()

    assert type(response) is list


def test_ag_07():
    agreement_id = test_helpers.get_parameter("/ag-07/agreement-id")

    response = ag_07.get_agreement_information(agreement_id)

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_ag_08():
    agreement_id = test_helpers.get_parameter("/ag-08/agreement-id")

    response = ag_08.get_agreement_information(agreement_id)

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_ag_09():
    response = ag_09.get_agreements()

    assert type(response) is list


def test_ag_10():
    agreement_id = test_helpers.get_parameter("/ag-10/agreement-id")

    response = ag_10.get_agreement_components(agreement_id)

    assert type(response) is list


def test_ag_13():
    agreement_id = test_helpers.get_parameter("/ag-13/agreement-id")

    response = ag_13.get_agreement(agreement_id)

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_ag_14():
    agreement_id = test_helpers.get_parameter("/ag-14/agreement-id")

    response = ag_14.get_agreement_information(agreement_id)

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def test_ag_15():
    agreement_id = test_helpers.get_parameter("/ag-15/agreement-id")

    response = ag_15.get_auto_renewal(agreement_id)

    assert type(response) is str


def test_ag_19():
    found_support = False

    agreement_id = test_helpers.get_parameter("/ag-19/agreement-id")

    response = ag_19.get_agreement_terms(agreement_id)

    for term in response["acceptedTerms"]:
        if "supportTerm" in term.keys():
            found_support = True

    assert found_support is True


def test_ag_20():
    found_freeTrialPricing = False

    agreement_id = test_helpers.get_parameter("/ag-20/agreement-id")

    response = ag_19.get_agreement_terms(agreement_id)

    for term in response["acceptedTerms"]:
        if "freeTrialPricingTerm" in term.keys():
            found_freeTrialPricing = True

    assert found_freeTrialPricing is True


def test_ag_31():
    response = ag_31.get_agreements()

    assert type(response) is list


def test_ag_32():
    agreement_id = test_helpers.get_parameter("/ag-32/agreement-id")

    response = ag_32.get_end_time_behavior(agreement_id)

    assert response is not None


def test_ag_33():
    agreement_id = test_helpers.get_parameter("/ag-33/agreement-id")

    response = ag_33.get_initial_agreement_id(agreement_id)

    # Always populated: it is the agreement's own id when the agreement starts the chain.
    assert type(response) is str


def test_ag_34():
    response = ag_34.get_agreements()

    assert type(response) is list


def test_ag_35():
    response = ag_35.get_agreements()

    assert type(response) is list


def test_ag_36():
    response = ag_36.get_agreements()

    assert type(response) is list
