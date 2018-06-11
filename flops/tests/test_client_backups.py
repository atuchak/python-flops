import pytest

from flops.exceptions import OperationError
from flops.tests.helpers import get_vm_backup_policy


def test_change_vm_backup_policy(flops_client, flops_vm_single):
    vm_id = flops_vm_single['id']
    quantity, frequency = 2, 72
    res = flops_client.change_vm_backup_policy(vm_id, quantity, frequency)
    assert res
    operation_id = res['operation_id']
    operation_result = flops_client.get_operation_status(operation_id)
    assert operation_result['operation_type'] == 'VM_BACKUP_POLICY_CHANGE'
    assert operation_result['status'] == 'DONE'

    res = get_vm_backup_policy(flops_client.get_vm(vm_id))
    assert res
    assert res['quantity'] == quantity
    assert res['frequency'] == frequency


def test_get_vm_backups(flops_client, flops_vm_single):
    vm_id = flops_vm_single['id']
    res = flops_client.get_vm_backups(vm_id)
    assert res == []


@pytest.mark.skip  # get_operation_status for 'rollback_vm_backup' throws OperationError
def test_rollback_vm_backup(flops_client, flops_vm_single):
    vm_id = flops_vm_single['id']
    res = flops_client.rollback_vm_backup(vm_id, backup=123)
    assert res
    operation_id = res['operation_id']
    with pytest.raises(OperationError):
        flops_client.get_operation_status(operation_id)
