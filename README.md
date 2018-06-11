# python-flops #

Python-flops is python lib to access [flops.ru](http://bit.ly/flops_ru) API

### Requirements
* Python (2.7, 3.4+)
* requests 


### Usage

#### Installation.
```bash
pip install flops
```

#### Credentials.
```python
from flops import FlopsClient

flops_client = FlopsClient(client_id='client_id', api_key='api_key')
tariffs = flops_client.get_tariffs()
```

#### FlopsClient methods.
```text
add_pubkey(self, name, public_key, tenant_id)


add_vm_ip(self, vm_id, tenant_id)


change_vm_backup_policy(self, vm_id, quantity, frequency, tenant_id)


change_vm_cpu(self, vm_id, cpu, tenant_id)


change_vm_disk(self, vm_id, disk, allow_restart, tenant_id, allow_memory_change)


change_vm_memory(self, vm_id, memory, allow_restart, tenant_id)


change_vm_password(self, vm_id, password, send_password, tenant_id)


change_vm_pubkeys(self, vm_id, key_ids, tenant_id)


clone_vm(self, vm_id, name, tenant_id, snapshot_id)


create_vm_snapshot(self, vm_id, name, description, tenant_id)


delete_pubkey(self, key_id, tenant_id)


delete_vm(self, vm_id, tenant_id)


delete_vm_ip(self, vm_id, ip, tenant_id)


delete_vm_snapshot(self, vm_id, snapshot_id, delete_children, tenant_id)


edit_pubkey(self, key_id, tenant_id, name, public_key)


get_distributions(self,)


get_distributions_by_name(self, name, match_type)


get_operation_status(self, operation_id)


get_pubkey(self, key_id)


get_pubkeys(self,)


get_pubkeys_by_name(self, name, match_type)


get_software(self,)


get_tariffs(self, for_windows, order_by, on_demand)


get_tenants(self,)


get_vm(self, vm_id)


get_vm_backups(self, vm_id)


get_vm_snapshots(self, vm_id)


get_vms(self,)


get_vms_by_name(self, name, match_type)


install_vm(self, name, distribution_id, tariff_id, tenant_id, memory, disk, cpu, ip_count, password, send_password, open_support_access, public_key_ids, software_ids)


move_vm_ip(self, vm_id, to_vm_id, ip, tenant_id)


poweroff_vm(self, vm_id, tenant_id)


reboot_vm(self, vm_id, tenant_id)


reinstall_vm(self, vm_id, name, distribution_id, tariff_id, tenant_id, memory, disk, cpu, password, send_password, open_support_access, public_key_ids, software_ids)


rename_vm(self, vm_id, new_name, tenant_id)


reset_vm(self, vm_id, tenant_id)


rollback_vm_backup(self, vm_id, backup, create_backup, tenant_id)


rollback_vm_snapshot(self, vm_id, snapshot_id, tenant_id)


shutdown_vm(self, vm_id, tenant_id)


start_vm(self, vm_id, tenant_id)


wait_for_operation(self, operation_id, timeout, polling_time)
```

### Testing

#### Install development requirements.
```bash
pip install pytest pytest-env tcpping2
```

#### Run the tests.
##### Warning: Your account could be charged for VMs creation
```bash
export CLIENT_ID=<CLIENT_ID>
export API_KEY=<API_KEY>
pytest flops/tests/*
```