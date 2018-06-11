from flops.exceptions import ValidationError


class FlopsValidator:
    create_params = {'name', 'tenant_id', 'distribution_id', 'tariff_id', 'memory', 'disk', 'cpu', 'ip_count',
                     'password', 'send_password', 'open_support_access', 'public_key_ids', 'software_ids'}

    @staticmethod
    def _validate_reinstall(vm_id, params):
        params = {k: v for k, v in params.items() if v is not None}

        if not str(vm_id).isdigit():
            raise ValidationError('vm_id: Идентификатор виртуального сервера, число, обязательный')

        if 'memory' in params and (params['memory'] > 16384 or params['memory'] < 512):
            raise ValidationError('memory: Pазмер RAM в мегабайтах. Минимальное значение — 512, максимальное — 16384.')

        if 'disk' in params and (params['disk'] > 524288 or params['disk'] < 8192):
            raise ValidationError('disk: Размер HDD в мегабайтах, число.'
                                  'При выборе фиксированного тарифа игнорируется.'
                                  'Минимальное значение — 8192, максимальное — 524288')

        if 'disk' in params and 'memory' in params and params['disk'] / params['memory'] > 64:
            raise ValidationError('Между размерами RAM и HDD должно выполняться условие HDD/RAM >= 64.')

        if 'cpu' in params and (params['cpu'] > 12 or params['cpu'] < 1):
            raise ValidationError('cpu: Количество процессорных ядер, число. При выборе фиксированного тарифа \ '
                                  'игнорируется. Минимальное значение — 1, максимальное — 12')

        if not isinstance(params['public_key_ids'], (list, tuple)):
            raise ValidationError('public_key_ids: Список публичных ключей')

        if not isinstance(params['software_ids'], (list, tuple)):
            raise ValidationError('software_ids: Список программного обеспечения')

        return {k: v for k, v in params.items() if v is not None}

    @staticmethod
    def _validate_create(params):
        params = {k: v for k, v in params.items() if v is not None}

        assert isinstance(params.get('tariff_id', ''), (str, int))  # TODO fix this

        if not params['name']:
            raise ValidationError('name: Введите имя виртуального сервера')

        if not str.isdigit(str(params['tenant_id'])):
            raise ValidationError('tenant_id: Идентификатор проекта, число, обязательный.')

        if not str.isdigit(str(params['distribution_id'])):
            raise ValidationError('distribution_id: Идентификатор дистрибутива, число, обязательный.')

        if 'memory' in params and (params['memory'] > 16384 or params['memory'] < 512):
            raise ValidationError('memory: Pазмер RAM в мегабайтах. Минимальное значение — 512, максимальное — 16384.')

        if 'disk' in params and (params['disk'] > 524288 or params['disk'] < 8192):
            raise ValidationError('disk: Размер HDD в мегабайтах, число.'
                                  'При выборе фиксированного тарифа игнорируется.'
                                  'Минимальное значение — 8192, максимальное — 524288')

        if 'disk' in params and 'memory' in params and params['disk'] / params['memory'] > 64:
            raise ValidationError('Между размерами RAM и HDD должно выполняться условие HDD/RAM >= 64.')

        if 'cpu' in params and (params['cpu'] > 12 or params['cpu'] < 1):
            raise ValidationError('cpu: Количество процессорных ядер, число. При выборе фиксированного тарифа \ '
                                  'игнорируется. Минимальное значение — 1, максимальное — 12')

        if not isinstance(params['public_key_ids'], (list, tuple)):
            raise ValidationError('public_key_ids: Список публичных ключей')

        if not isinstance(params['software_ids'], (list, tuple)):
            raise ValidationError('software_ids: Список программного обеспечения')

        return {k: v for k, v in params.items() if v is not None}

    @staticmethod
    def _validate_change_backup_policy(quantity, frequency):
        data = {}

        if not quantity or quantity < 1 or quantity > 10:
            raise ValidationError('quantity: Количество хранимых копий, число, обязательный. '
                                  'Минимальное значение — 1, максимальное — 10.')
        data['quantity'] = quantity

        if not frequency or frequency not in {3, 6, 12, 24, 72}:
            raise ValidationError('frequency: Интервал между копиями в часах, число, обязательный. '
                                  'Одно из значений: 3, 6, 12, 24, 72.')
        data['frequency'] = frequency

        return data
