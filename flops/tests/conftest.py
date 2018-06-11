import os
import pytest

from flops.client import FlopsClient
from flops.exceptions import NotFoundError
from flops.tests.helpers import generate_name, generate_password

client_id = os.environ.get('CLIENT_ID', '')
api_key = os.environ.get('API_KEY', '')


def cleanup_test_vms(fc):
    vms = fc.get_vms_by_name('__test', match_type='startswith')
    for vm in vms:
        fc.delete_vm(vm['id'])


def cleanup_test_pubkeys(fc):
    pub_keys = fc.get_pubkeys_by_name('__test', match_type='startswith')
    for pub_key in pub_keys:
        fc.delete_pubkey(pub_key['id'])


@pytest.fixture(scope='session')
def flops_client():
    fc = FlopsClient(client_id, api_key)
    yield fc
    cleanup_test_vms(fc)
    cleanup_test_pubkeys(fc)


@pytest.fixture(scope='session')
def flops_debian_distributions(flops_client):
    yield flops_client.get_distributions_by_name(name='debian')


@pytest.fixture(scope='session')
def flops_linux_tariffs(flops_client):
    yield flops_client.get_tariffs(for_windows=False, order_by='memory')


@pytest.fixture(scope='function')
def flops_vm(flops_client, flops_debian_distributions, flops_linux_tariffs):
    name = generate_name('__test_flops_vm')
    distribution = flops_debian_distributions[-1]
    distribution_id = distribution['id']
    tariff = flops_linux_tariffs[0]
    tariff_id = tariff['id']

    res = flops_client.install_vm(name=name, distribution_id=distribution_id,
                                  tariff_id=tariff_id, send_password=False,
                                  password=generate_password(32))  # password is required for send_password=False
    operation_id = res['operation_id']
    vm_id = res['vm_id']
    flops_client.wait_for_operation(operation_id, timeout=5)
    yield flops_client.get_vm(vm_id)
    try:
        flops_client.delete_pubkey(vm_id)
    except NotFoundError:
        pass


@pytest.fixture(scope='session')
def flops_vm_single(flops_client, flops_debian_distributions):
    name = generate_name('__test_flops_vm_session')
    distribution = flops_debian_distributions[-1]
    distribution_id = distribution['id']
    tariff = flops_client.get_tariffs(on_demand=True, for_windows=False)[0]
    tariff_id = tariff['id']

    res = flops_client.install_vm(name=name, distribution_id=distribution_id,
                                  tariff_id=tariff_id, send_password=False,
                                  password=generate_password(32), disk=8192, memory=512, cpu=1, ip_count=1)
    operation_id = res['operation_id']
    vm_id = res['vm_id']
    flops_client.wait_for_operation(operation_id, timeout=10)
    yield flops_client.get_vm(vm_id)
    try:
        flops_client.delete_pubkey(vm_id)
    except NotFoundError:
        pass


@pytest.fixture(scope='session')
def flops_2nd_vm_single(flops_client, flops_debian_distributions):
    name = generate_name('__test_flops_2nd_vm_session')
    distribution = flops_debian_distributions[-1]
    distribution_id = distribution['id']
    tariff = flops_client.get_tariffs(on_demand=True, for_windows=False)[0]
    tariff_id = tariff['id']

    res = flops_client.install_vm(name=name, distribution_id=distribution_id,
                                  tariff_id=tariff_id, send_password=False,
                                  password=generate_password(32), disk=8192, memory=512, cpu=1, ip_count=1)
    operation_id = res['operation_id']
    vm_id = res['vm_id']
    flops_client.wait_for_operation(operation_id, timeout=10)
    yield flops_client.get_vm(vm_id)
    try:
        flops_client.delete_pubkey(vm_id)
    except NotFoundError:
        pass
