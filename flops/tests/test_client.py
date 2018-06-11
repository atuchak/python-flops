import pytest

from flops import FlopsClient
from flops.exceptions import AuthError, NotFoundError, ApiError


def test_auth():
    client_id = '123'
    api_key = '123'
    fc = FlopsClient(client_id, api_key)

    with pytest.raises(AuthError):
        fc.get_tenants()


def test_get_tariffs(flops_client):
    res = flops_client.get_tariffs()
    assert res
    assert type(res) is list
    assert len(res) >= 1


def test_get_tenants(flops_client):
    res = flops_client.get_tenants()
    assert res
    assert isinstance(res, list)
    assert len(res) >= 1


def test_get_all_distributions(flops_client):
    res = flops_client.get_distributions()
    assert res
    assert isinstance(res, list)
    assert len(res) >= 1


def test_get_software(flops_client):
    res = flops_client.get_software()
    assert res
    assert isinstance(res, list)
    assert len(res) >= 1


def test_get_operation_status(flops_client):
    res = flops_client.get_operation_status(operation_id=1)
    assert res
    assert isinstance(res, dict)

    with pytest.raises(NotFoundError):
        operation_id = int('9' * 10)
        flops_client.get_operation_status(operation_id)

        # error.object.not.found
        # with pytest.raises(ApiError):
        #     operation_id = int('9' * 100)
        #     flops_client.get_operation_status(operation_id)
