from datetime import datetime, timedelta
from time import sleep

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

import requests

from flops.exceptions import (
    ValidationError, AuthError, NotFoundError, ApiError, OperationTimeoutError,
    OperationError, ApiLimitError,
)
from flops.helpers import transform_dict_keys_to_underscore, underscore_to_camelcase, order_list_by_dict_key
from flops.validators import FlopsValidator


class BaseAPI:
    endpoint = 'https://api.flops.ru/api/v1/'

    def __init__(self, client_id='', api_key='', **kwargs):
        self.client_id = client_id
        self.api_key = api_key
        self._session = requests.Session()

        for attr, attr_value in kwargs.items():
            setattr(self, attr, attr_value)

    @staticmethod
    def _process_errors(error_message, error_code, field_errors):
        if error_code == 'error.not.owner':
            raise AuthError(error_message)

        elif error_code == 'error.object.not.found':
            raise NotFoundError(error_message)

        elif error_code == 'error.vm.not.found':
            raise NotFoundError(error_message)

        elif error_code == 'unexpected.exception':
            raise ApiError(error_message)

        elif error_code == 'vm.limit.exceed':
            raise ApiLimitError(error_message)

        elif error_code == 'error.vm.volume.under.operation':
            raise OperationError(error_message)

        elif error_code == 'error.operation.already.started':
            raise OperationError(error_message)

        elif error_code is None and field_errors:
            raise ValidationError(str(field_errors) + error_message)

        raise ApiError(error_message)

    def _process_response(self, response):
        if response.status_code != 200:
            raise ApiError

        data = response.json()
        data = transform_dict_keys_to_underscore(data)

        if data['status'] == 'ERROR':
            error_code = data.get('error_code')
            field_errors = data.get('field_errors')  # reinstall_vm
            self._process_errors(error_code=error_code, error_message=data['error_message'], field_errors=field_errors)

        elif 'result' in data and isinstance(data['result'], dict) and data['result'].get('status') == 'ERROR':
            error_code = data['result'].get('error_code')
            error_message = data['result'].get('error_message')
            self._process_errors(error_code=error_code, error_message=error_message, field_errors='')

        return transform_dict_keys_to_underscore(data)

    def _perform_request(self, url, params=None):
        if params is None:
            params = {}

        if not self.client_id or not self.api_key:
            raise AuthError("client_id or  api_key is not valid")

        url = urljoin(self.endpoint, url)
        params.update({'client_id': self.client_id, 'api_key': self.api_key})
        params = {underscore_to_camelcase(k): v for k, v in params.items()}
        headers = {'Content-type': 'application/json'}
        response = self._session.get(url, params=params, headers=headers)
        return self._process_response(response)

    def get_tenants(self):
        return self._perform_request('tenant')['result']

    def _get_default_tenant_id(self):
        return self.get_tenants()[0]['id']

    def get_tariffs(self, for_windows=None, order_by=None, on_demand=None):
        result = self._perform_request('tariffs')['result']

        if for_windows is not None:
            result = [r for r in result if r['for_windows'] == for_windows]
        if on_demand is not None:
            result = [r for r in result if r['on_demand'] == on_demand]
        if order_by:
            result = order_list_by_dict_key(result, key=order_by)
        return result

    def get_distributions(self):
        return self._perform_request('distribution')['result']

    def get_distributions_by_name(self, name, match_type='equal'):
        distributions = self.get_distributions()

        name = name.lower()
        match_types = {
            'equal': (pk for pk in distributions if pk['name'].lower() == name),
            'startswith': (pk for pk in distributions if pk['name'].startswith(name)),
            'endswith': (pk for pk in distributions if pk['name'].endswith(name)),
        }
        return list(match_types.get(match_type, 'equal'))

    def get_software(self):
        return self._perform_request('software')['result']

    def get_operation_status(self, operation_id):
        return self._perform_request('operation/{}/'.format(operation_id))['result']

    def wait_for_operation(self, operation_id, timeout=None, polling_time=0.5):
        started_at = datetime.now()
        while True:
            res = self.get_operation_status(operation_id)
            if res['status'].lower() == 'done':
                return res
            if timeout and datetime.now() - started_at > timedelta(seconds=timeout):
                raise OperationTimeoutError
            sleep(polling_time)

    def _get_tenant_id(self, tenant_id, vm_id):
        if tenant_id:
            return tenant_id
        else:
            return self._get_vm_tenant_id(vm_id)

    def _default_tenant_id(self, tenant_id):
        if tenant_id:
            return tenant_id
        else:
            return self._get_default_tenant_id()


class PublicKey(BaseAPI):
    def get_pubkeys(self):
        return self._perform_request('pubkeys')['result']

    def get_pubkey(self, key_id):
        public_keys = self.get_pubkeys()
        for pk in public_keys:
            if key_id == pk['id']:
                return pk

        raise NotFoundError

    def get_pubkeys_by_name(self, name, match_type='equal'):
        if name == '':
            return
        public_keys = self.get_pubkeys()
        match_types = {
            'equal': [pk for pk in public_keys if pk['name'] == name],
            'startswith': [pk for pk in public_keys if pk['name'].startswith(name)],
        }
        return match_types.get(match_type, 'equal')

    def add_pubkey(self, name, public_key, tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_default_tenant_id()

        params = {'tenant_id': tenant_id, 'name': name, 'public_key': public_key}
        return self._perform_request('pubkeys/add', params=params)['result']

    def edit_pubkey(self, key_id, tenant_id=None, name=None, public_key=None):
        if not tenant_id:
            tenant_id = self._get_default_tenant_id()

        params = {'tenant_id': tenant_id}
        if name:
            params['name'] = name
        if public_key:
            params['public_key'] = public_key

        return self._perform_request('pubkeys/{}/edit'.format(key_id), params=params)['result']

    def delete_pubkey(self, key_id, tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_default_tenant_id()

        params = {'tenant_id': tenant_id}

        return self._perform_request('pubkeys/{}/delete'.format(key_id), params=params)


class Backup(BaseAPI, FlopsValidator):
    def get_vm_backups(self, vm_id):
        return self._perform_request('vm/{}/backups'.format(vm_id))['result']

    def change_vm_backup_policy(self, vm_id, quantity=None, frequency=None, tenant_id=None):
        params = self._validate_change_backup_policy(quantity, frequency)
        params.update({'tenant_id': self._default_tenant_id(tenant_id)})
        return self._perform_request('vm/{}/backup_policy_change'.format(vm_id), params=params)

    def rollback_vm_backup(self, vm_id, backup, create_backup=True, tenant_id=None):
        params = {
            'tenant_id': self._get_tenant_id(tenant_id, vm_id),
            'backup': backup, 'create_backup': create_backup,
        }
        return self._perform_request('vm/{}/backup_rollback'.format(vm_id), params=params)


class Snapshot(BaseAPI):
    def get_vm_snapshots(self, vm_id):
        return self._perform_request('vm/{}/snapshots/'.format(vm_id), params={})['result']

    def create_vm_snapshot(self, vm_id, name, description='', tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_vm_tenant_id(vm_id)

        params = {'tenant_id': tenant_id, 'name': name, 'description': description}
        return self._perform_request('vm/{}/snapshot_create/'.format(vm_id), params=params)

    def rollback_vm_snapshot(self, vm_id, snapshot_id, tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_vm_tenant_id(vm_id)

        params = {'tenant_id': tenant_id, 'snapshot_id': snapshot_id}
        return self._perform_request('vm/{}/snapshot_rollback/'.format(vm_id), params=params)

    def delete_vm_snapshot(self, vm_id, snapshot_id, delete_children=False, tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_vm_tenant_id(vm_id)

        params = {'tenant_id': tenant_id, 'snapshot_id': snapshot_id, 'delete_children': delete_children}
        return self._perform_request('vm/{}/snapshot_delete/'.format(vm_id), params=params)


class VM(BaseAPI, FlopsValidator):
    def get_vms(self):
        return self._perform_request('vm')['result']

    def get_vms_by_name(self, name, match_type='equal'):
        if name == '':
            return

        vms = self.get_vms()
        match_types = {
            'equal': [vm for vm in vms if vm['name'] == name],
            'startswith': [vm for vm in vms if vm['name'].startswith(name)],
        }
        return match_types.get(match_type, 'equal')

    def install_vm(self, name='', distribution_id=None, tariff_id=None, tenant_id=None, memory=None,
                   disk=None, cpu=None, ip_count=None, password=None, send_password=True, open_support_access=False,
                   public_key_ids=[], software_ids=[]):

        if not tenant_id:
            tenant_id = self._get_default_tenant_id()

        if isinstance(public_key_ids, (str, int)):
            public_key_ids = [public_key_ids, ]

        if isinstance(software_ids, (str, int)):
            software_ids = [software_ids, ]

        params = {k: v for k, v in locals().items() if k in self.create_params}
        params = self._validate_create(params)

        resp = self._perform_request('vm/install/', params=params)
        resp['vm_id'] = resp.pop('result')
        return resp

    def clone_vm(self, vm_id, name, tenant_id=None, snapshot_id=None):
        params = {}
        if not tenant_id:
            params['tenant_id'] = self._get_default_tenant_id()
        if snapshot_id:
            params[snapshot_id] = snapshot_id
        params.update({'vm_id': vm_id, 'name': name})
        return self._perform_request('vm/{}/clone/'.format(vm_id), params=params)

    def reinstall_vm(self, vm_id, name=None, distribution_id=None, tariff_id=None, tenant_id=None, memory=None,
                     disk=None, cpu=None, password=None, send_password=True, open_support_access=False,
                     public_key_ids=[], software_ids=[]):
        """
        :return: {'operation_id': 431590, 'status': 'OK'}
        """
        if not tenant_id:
            tenant_id = self._get_default_tenant_id()

        if isinstance(public_key_ids, (str, int)):
            public_key_ids = [public_key_ids, ]

        if isinstance(software_ids, (str, int)):
            software_ids = [software_ids, ]

        params = {k: v for k, v in locals().items() if k in self.create_params}  # TODO
        params = self._validate_reinstall(vm_id, params)
        return self._perform_request('vm/{}/reinstall/'.format(vm_id), params=params)

    def get_vm(self, vm_id):
        return self._perform_request('vm/{}/'.format(vm_id))['result']

    def _get_vm_tenant_id(self, vm_id):
        return self.get_vm(vm_id)['tenant_id']

    def rename_vm(self, vm_id, new_name, tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_vm_tenant_id(vm_id)

        params = {'name': new_name, 'tenant_id': tenant_id}
        return self._perform_request('vm/{}/rename/'.format(vm_id), params=params)

    def start_vm(self, vm_id, tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_vm_tenant_id(vm_id)

        params = {'tenant_id': tenant_id}
        return self._perform_request('vm/{}/start/'.format(vm_id), params=params)

    def reset_vm(self, vm_id, tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_vm_tenant_id(vm_id)

        params = {'tenant_id': tenant_id}
        return self._perform_request('vm/{}/reset/'.format(vm_id), params=params)

    def reboot_vm(self, vm_id, tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_vm_tenant_id(vm_id)

        params = {'tenant_id': tenant_id}
        return self._perform_request('vm/{}/reboot/'.format(vm_id), params=params)

    def poweroff_vm(self, vm_id, tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_vm_tenant_id(vm_id)

        params = {'tenant_id': tenant_id}
        return self._perform_request('vm/{}/poweroff/'.format(vm_id), params=params)

    def shutdown_vm(self, vm_id, tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_vm_tenant_id(vm_id)

        params = {'tenant_id': tenant_id}
        return self._perform_request('vm/{}/shutdown/'.format(vm_id), params=params)

    def delete_vm(self, vm_id, tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_vm_tenant_id(vm_id)

        params = {'tenant_id': tenant_id}
        return self._perform_request('vm/{}/delete/'.format(vm_id), params=params)

    def change_vm_password(self, vm_id, password, send_password=False, tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_vm_tenant_id(vm_id)

        params = {'tenant_id': tenant_id, 'password': password, 'send_password': send_password}
        return self._perform_request('vm/{}/password_change/'.format(vm_id), params=params)

    def change_vm_pubkeys(self, vm_id, key_ids=[], tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_vm_tenant_id(vm_id)

        params = {'tenant_id': tenant_id, 'key_ids': key_ids}
        return self._perform_request('vm/{}/pubkey_change/'.format(vm_id), params=params)


class VMResources:
    def change_vm_memory(self, vm_id, memory, allow_restart=False, tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_vm_tenant_id(vm_id)

        params = {'tenant_id': tenant_id, 'memory': memory, 'allow_restart': allow_restart}
        # TODO validate (Минимальное значение — 512, максимальное — 16384)
        return self._perform_request('vm/{}/memory_change/'.format(vm_id), params=params)

    def change_vm_disk(self, vm_id, disk, allow_restart=False, tenant_id=None, allow_memory_change=False):
        if not tenant_id:
            tenant_id = self._get_vm_tenant_id(vm_id)

        params = {
            'tenant_id': tenant_id, 'disk': disk,
            'allow_restart': allow_restart, 'allow_memory_change': allow_memory_change,
        }
        # TODO (размер HDD в мегабайтах, число, обязательный. Минимальное значение — 8192, максимальное — 524288)
        return self._perform_request('vm/{}/disk_change/'.format(vm_id), params=params)

    def change_vm_cpu(self, vm_id, cpu, tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_vm_tenant_id(vm_id)

        params = {'tenant_id': tenant_id, 'cpu': cpu}
        # TODO valodate (количество процессорных ядер, число, обязательный. Минимальное значение — 1, максимальное — 12)
        return self._perform_request('vm/{}/cpu_change/'.format(vm_id), params=params)

    def add_vm_ip(self, vm_id, tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_vm_tenant_id(vm_id)

        params = {'tenant_id': tenant_id}
        return self._perform_request('vm/{}/ip_add/'.format(vm_id), params=params)

    def delete_vm_ip(self, vm_id, ip, tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_vm_tenant_id(vm_id)

        params = {'tenant_id': tenant_id, 'ip': ip}
        return self._perform_request('vm/{}/ip_delete/'.format(vm_id), params=params)

    def move_vm_ip(self, vm_id, to_vm_id, ip, tenant_id=None):
        if not tenant_id:
            tenant_id = self._get_vm_tenant_id(vm_id)

        params = {'tenant_id': tenant_id, 'to_vm_id': to_vm_id, 'ip': ip}
        return self._perform_request('vm/{}/ip_move/'.format(vm_id), params=params)


class FlopsClient(VM, VMResources, Backup, PublicKey, Snapshot):
    pass
