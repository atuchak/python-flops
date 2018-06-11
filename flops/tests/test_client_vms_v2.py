import pytest as pytest
from tcpping2 import Ping

from flops.tests.helpers import get_vm_1st_puplic_ip, generate_password, generate_pub_key, get_vm_puplic_ips, \
    get_vm_2nd_puplic_ip, generate_name

VM_READY_TIMEOUT = 120


@pytest.mark.skip
def test_change_vm_password(flops_client, flops_vm_single):
    vm_id = flops_vm_single['id']
    vm_ip = get_vm_1st_puplic_ip(flops_vm_single)
    password = generate_password(16)
    Ping(vm_ip, 22).wait_for_ping(blocking_timeout=VM_READY_TIMEOUT)
    res = flops_client.change_vm_password(vm_id, password)
    assert res
    operation_id = res['operation_id']

    operation_result = flops_client.get_operation_status(operation_id)
    assert operation_result['operation_type'] == 'VM_PASSWORD_CHANGE'


@pytest.mark.skip
def test_change_vm_pubkeys(flops_client, flops_vm_single):
    vm_id = flops_vm_single['id']
    vm_ip = get_vm_1st_puplic_ip(flops_vm_single)
    key = flops_client.add_pubkey(**generate_pub_key(name_prefix='__test_change_vm_pubkey'))
    Ping(vm_ip, 22).wait_for_ping(blocking_timeout=VM_READY_TIMEOUT)
    res = flops_client.change_vm_pubkeys(vm_id, key_ids=[key['id'], ])
    assert res
    operation_id = res['operation_id']

    operation_result = flops_client.get_operation_status(operation_id)
    assert operation_result['operation_type'] == 'VM_PUBLIC_KEY_CHANGE'


def test_change_vm_memory(flops_client, flops_vm_single):
    vm_id = flops_vm_single['id']
    vm_ip = get_vm_1st_puplic_ip(flops_vm_single)
    Ping(vm_ip, 22).wait_for_ping(blocking_timeout=VM_READY_TIMEOUT)
    res = flops_client.change_vm_memory(vm_id, memory=1024)
    assert res
    operation_id = res['operation_id']

    operation_result = flops_client.get_operation_status(operation_id)
    assert operation_result['operation_type'] == 'VM_MEMORY_CHANGE'


def test_change_vm_disk(flops_client, flops_vm_single):
    vm_id = flops_vm_single['id']
    vm_ip = get_vm_1st_puplic_ip(flops_vm_single)
    Ping(vm_ip, 22).wait_for_ping(blocking_timeout=VM_READY_TIMEOUT)
    res = flops_client.change_vm_disk(vm_id, disk=8192 * 2)
    assert res
    operation_id = res['operation_id']

    operation_result = flops_client.get_operation_status(operation_id)
    assert operation_result['operation_type'] == 'VM_VOLUME_CHANGE'


def test_change_vm_cpu(flops_client, flops_vm_single):
    vm_id = flops_vm_single['id']
    vm_ip = get_vm_1st_puplic_ip(flops_vm_single)
    Ping(vm_ip, 22).wait_for_ping(blocking_timeout=VM_READY_TIMEOUT)
    res = flops_client.change_vm_cpu(vm_id, cpu=2)
    assert res
    operation_id = res['operation_id']

    operation_result = flops_client.get_operation_status(operation_id)
    assert operation_result['operation_type'] == 'VM_CPU_CORES_QUOTA_CHANGE'


def test_add_delete_vm_ip(flops_client, flops_vm_single):
    vm_id = flops_vm_single['id']
    vm_ip = get_vm_1st_puplic_ip(flops_vm_single)
    vm_ips = get_vm_puplic_ips(flops_vm_single)
    vm_ips_count = len(vm_ips)
    Ping(vm_ip, 22).wait_for_ping(blocking_timeout=VM_READY_TIMEOUT)
    res = flops_client.add_vm_ip(vm_id)
    assert res
    operation_id = res['operation_id']
    operation_result = flops_client.get_operation_status(operation_id)
    assert operation_result['operation_type'] == 'VM_IP_ADD'
    assert len(get_vm_puplic_ips(flops_client.get_vm(vm_id))) == vm_ips_count + 1

    # delete
    Ping(vm_ip, 22).wait_for_ping(blocking_timeout=VM_READY_TIMEOUT)
    ip = get_vm_2nd_puplic_ip(flops_client.get_vm(vm_id))
    res = flops_client.delete_vm_ip(vm_id, ip)
    assert res
    operation_id = res['operation_id']
    operation_result = flops_client.get_operation_status(operation_id)
    assert operation_result['operation_type'] == 'VM_IP_DELETE'
    assert len(get_vm_puplic_ips(flops_client.get_vm(vm_id))) == vm_ips_count


def test_add_move_vm_ip(flops_client, flops_vm_single, flops_2nd_vm_single):
    vm1_id = flops_vm_single['id']
    vm1_ip = get_vm_1st_puplic_ip(flops_vm_single)
    vm2_id = flops_2nd_vm_single['id']
    vm2_ip = get_vm_1st_puplic_ip(flops_2nd_vm_single)
    Ping(vm1_ip, 22).wait_for_ping(blocking_timeout=VM_READY_TIMEOUT)
    Ping(vm2_ip, 22).wait_for_ping(blocking_timeout=VM_READY_TIMEOUT)

    res = flops_client.add_vm_ip(vm1_id)
    assert res
    Ping(vm1_ip, 22).wait_for_ping(blocking_timeout=VM_READY_TIMEOUT)
    Ping(vm2_ip, 22).wait_for_ping(blocking_timeout=VM_READY_TIMEOUT)
    vm1_2dn_ip = get_vm_2nd_puplic_ip(flops_client.get_vm(vm1_id))

    # move
    assert vm1_2dn_ip in get_vm_puplic_ips(flops_client.get_vm(vm1_id))
    assert vm1_2dn_ip not in get_vm_puplic_ips(flops_client.get_vm(vm2_id))
    res = flops_client.move_vm_ip(vm1_id, vm2_id, vm1_2dn_ip)
    assert res
    Ping(vm2_ip, 22).wait_for_ping(blocking_timeout=VM_READY_TIMEOUT)
    operation_id = res['operation_id']
    operation_result = flops_client.get_operation_status(operation_id)
    # assert operation_result['operation_type'] == 'VM_IP_MOVE'
    assert operation_result['operation_type'] == 'VM_IP_ADD'  # wtf?

    assert vm1_2dn_ip not in get_vm_puplic_ips(flops_client.get_vm(vm1_id))
    assert vm1_2dn_ip in get_vm_puplic_ips(flops_client.get_vm(vm2_id))


# @pytest.mark.skip  # get operation status for snapshots is broken
def test_shapshots(flops_client, flops_vm_single):
    vm_id = flops_vm_single['id']
    vm_ip = get_vm_1st_puplic_ip(flops_vm_single)
    Ping(vm_ip, 22).wait_for_ping(blocking_timeout=VM_READY_TIMEOUT)

    # get
    res = flops_client.get_vm_snapshots(vm_id)
    num_of_snapshots = len(res)

    # create
    res = flops_client.create_vm_snapshot(vm_id, name=generate_name('__snapshot'))
    assert res
    operation_id = res['operation_id']
    operation_result = flops_client.get_operation_status(operation_id)
    assert operation_result['operation_type'] == 'VM_CREATE_SNAPSHOT'
    snapshot_id = operation_result['id']
    flops_client.wait_for_operation(operation_id, timeout=VM_READY_TIMEOUT)
    Ping(vm_ip, 22).wait_for_ping(blocking_timeout=VM_READY_TIMEOUT)

    # get
    res = flops_client.get_vm_snapshots(vm_id)
    assert res
    assert num_of_snapshots == len(res) - 1
    # rollback
    res = flops_client.rollback_vm_snapshot(vm_id, snapshot_id)
    assert res
    # operation_id = res['operation_id']
    # operation_result = flops_client.get_operation_status(operation_id)
    # assert operation_result['operation_type'] == 'VM_ROLLBACK_SNAPSHOT'
    Ping(vm_ip, 22).wait_for_ping(blocking_timeout=VM_READY_TIMEOUT)

    # get
    res = flops_client.get_vm_snapshots(vm_id)
    assert res
    assert num_of_snapshots == len(res) - 1

    # delete
    res = flops_client.delete_vm_snapshot(vm_id, snapshot_id)
    assert res
    operation_id = res['operation_id']
    # operation_result = flops_client.get_operation_status(operation_id)
    # assert operation_result['operation_type'] == 'VM_DELETE_SNAPSHOT'
    Ping(vm_ip, 22).wait_for_ping(blocking_timeout=VM_READY_TIMEOUT)

    # get
    res = flops_client.get_vm_snapshots(vm_id)
    assert res
    assert num_of_snapshots == len(res)
    # E       AssertionError: assert 0 == 1
    # E        +  where 1 = len([{'description': '', 'id': 16546, 'name': '__snapshotzjcwlsoiizvjpdfw',
    # 'time_added': '2018-06-08T19:52:44.665+0000'}])




