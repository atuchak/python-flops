import pytest

from flops.exceptions import OperationError
from flops.tests.helpers import generate_name, generate_password

OPERATION_TIMEOUT = 5
SHUTDOWN_TIMEOUT = 120


def test_install_vm(flops_client, flops_debian_distributions, flops_linux_tariffs):
    name = '__test_install_vm'
    distribution = flops_debian_distributions[-1]
    distribution_id = distribution['id']
    tariff = flops_linux_tariffs[0]
    tariff_id = tariff['id']

    res_install = flops_client.install_vm(name=name, distribution_id=distribution_id, tariff_id=tariff_id,
                                          send_password=False, password=generate_password(32), public_key_ids=[])

    assert res_install
    operation_id = res_install['operation_id']
    vm_id = res_install['vm_id']

    operation_result = flops_client.wait_for_operation(operation_id, timeout=OPERATION_TIMEOUT)
    assert operation_result
    assert operation_result['id'] == operation_id
    assert operation_result['percentage'] == 100
    assert operation_result['vm_id'] == vm_id
    assert operation_result['operation_type'] == 'VM_INSTALL'

    res_get = flops_client.get_vm(vm_id)
    assert res_get
    assert res_get['id'] == vm_id
    assert res_get['name'] == name
    assert res_get['tariff_id'] == tariff_id
    assert res_get['cpu'] == tariff['cpu']
    assert res_get['disk'] == tariff['disk']
    assert res_get['memory'] == tariff['memory']


def test_clone_vm(flops_client, flops_vm):
    clone_name = generate_name('__test_clone_vm')

    res_clone = flops_client.clone_vm(vm_id=flops_vm['id'], name=clone_name)
    assert res_clone
    operation_id = res_clone['operation_id']

    operation_result = flops_client.wait_for_operation(operation_id, timeout=OPERATION_TIMEOUT)
    assert operation_result
    clone_vm_id = operation_result['vm_id']
    assert operation_result['operation_type'] == 'VM_CLONE'
    assert operation_result['percentage'] == 100

    clone_vm = flops_client.get_vm(vm_id=clone_vm_id)
    del_fields = ['id', 'time_added', 'state', 'private_ip_address', 'name', 'internal_id', 'ip_addresses']
    for field in del_fields:
        del flops_vm[field]
        del clone_vm[field]

    assert flops_vm == clone_vm


# def test_clone_vm_from_snapshot(flops_client, flops_vm):
#     TODO

def test_reinstall_vm(flops_client, flops_debian_distributions, flops_linux_tariffs, flops_vm):
    vm_id = flops_vm['id']
    new_name = generate_name('__test_reinstall_vm')
    distribution = flops_debian_distributions[1]
    new_distribution_id = distribution['id']
    new_tariff = flops_linux_tariffs[3]  # TODO fix type, has bug if tariff_id is dict
    assert new_distribution_id != flops_vm['distribution']['id']
    assert new_tariff['id'] != flops_vm['tariff_id']

    reinstall_res = flops_client.reinstall_vm(
        vm_id, name=new_name, distribution_id=new_distribution_id, tariff_id=new_tariff['id'],
        send_password=False, open_support_access=False,
    )
    assert reinstall_res
    operation_id = reinstall_res['operation_id']

    operation_result = flops_client.wait_for_operation(operation_id, timeout=OPERATION_TIMEOUT)
    assert operation_result
    assert operation_result['percentage'] == 100
    assert operation_result['operation_type'] == 'VM_REINSTALL'
    assert operation_result['vm_id'] == vm_id

    get_res = flops_client.get_vm(vm_id)
    assert get_res['distribution']['id'] == new_distribution_id
    assert get_res['name'] == new_name
    assert get_res['cpu'] == new_tariff['cpu']
    assert get_res['disk'] == new_tariff['disk']


def test_rename_vm(flops_client, flops_vm):
    vm_id = flops_vm['id']
    new_name = generate_name('__test_rename_vm')
    res = flops_client.rename_vm(vm_id, new_name=new_name)
    assert res
    operation_id = res['operation_id']
    operation_result = flops_client.wait_for_operation(operation_id, timeout=OPERATION_TIMEOUT)
    assert operation_result['operation_type'] == 'VM_UPDATE'
    assert operation_result['vm_id'] == vm_id


def test_poweroff_start_vm(flops_client, flops_vm):
    vm_id = flops_vm['id']
    assert flops_vm['state'] == 'VIR_DOMAIN_RUNNING'

    res = flops_client.poweroff_vm(vm_id)
    assert res
    operation_id = res['operation_id']
    operation_result = flops_client.wait_for_operation(operation_id, timeout=OPERATION_TIMEOUT)
    assert operation_result
    assert operation_result['operation_type'] == 'VM_DESTROY'
    assert operation_result['percentage'] == 100

    res = flops_client.get_vm(vm_id)
    assert res['state'] == 'VIR_DOMAIN_SHUTOFF'

    res = flops_client.start_vm(vm_id)
    assert res
    operation_id = res['operation_id']
    operation_result = flops_client.wait_for_operation(operation_id, timeout=OPERATION_TIMEOUT)
    assert operation_result
    assert operation_result['operation_type'] == 'VM_START'
    assert operation_result['percentage'] == 100

    res = flops_client.get_vm(vm_id)
    assert res['state'] == 'VIR_DOMAIN_RUNNING'


def test_shutdown_vm(flops_client, flops_vm):
    """useless due to async nature of the process"""
    vm_id = flops_vm['id']
    assert flops_vm['state'] == 'VIR_DOMAIN_RUNNING'

    res = flops_client.shutdown_vm(vm_id)
    assert res
    operation_id = res['operation_id']
    operation_result = flops_client.get_operation_status(operation_id)
    assert operation_result
    assert operation_result['operation_type'] == 'VM_SHUTDOWN'


def test_reset_vm(flops_client, flops_vm):
    vm_id = flops_vm['id']
    assert flops_vm['state'] == 'VIR_DOMAIN_RUNNING'

    res = flops_client.reset_vm(vm_id)
    assert res
    operation_id = res['operation_id']
    operation_result = flops_client.wait_for_operation(operation_id, timeout=OPERATION_TIMEOUT)
    assert operation_result
    assert operation_result['operation_type'] == 'VM_RESET'
    assert operation_result['percentage'] == 100


@pytest.mark.skip
def test_reboot_vm(flops_client, flops_vm):
    """useless due to async nature of the process"""
    vm_id = flops_vm['id']
    assert flops_vm['state'] == 'VIR_DOMAIN_RUNNING'

    res = flops_client.reboot_vm(vm_id)
    assert res
    operation_id = res['operation_id']
    operation_result = flops_client.get_operation_status(operation_id)
    assert operation_result
    assert operation_result['operation_type'] == 'VM_REBOOT'

    # cleanup
    with pytest.raises(OperationError):
        flops_client.delete_vm(vm_id)
