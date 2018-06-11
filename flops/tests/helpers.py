import random
import string


def generate_str(length):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def generate_password(length):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length - 2)) + '2!'


def generate_pub_key(name_prefix):
    public_key = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCssArt8UYrTB0Rvh9S95A18KTpZMgVZ45sPYxFgKAQnZiI1' \
                 'eT1+2Bfva2xJHYPFJSOfe3QHhW9CLevYcyxcQnlOMbQmmI6nkQfYoajsYiVesHf3uFX3OI3gFuUUoo7fQ1DdY' \
                 'f663DS1wbDY13DzrrzNX18Nc7JKo5wua9bL++akWnwRkUApuJvZA2BockHhf2SWsLzE7K6jaoL2Ist90mRMH7' \
                 'ut4gPxjphYzdhBdGmP5V8lLX67rJ+r9LKKPM1sG9tnxctVf9ps0XQ7gPY3yFmNP9l+wrKsV1nJf8SYKs4M3ME' \
                 '8eYdnkEtE2YXxu/{}'
    return {'name': name_prefix + generate_str(16), 'public_key': public_key.format(generate_str(25))}


def generate_pub_keys(name_prefix, num):
    return [generate_pub_key(name_prefix) for _ in range(num)]


def generate_name(name_prefix='__test'):
    return name_prefix + generate_str(16)


def get_vm_puplic_ips(vm):
    return vm['ip_addresses']


def get_vm_1st_puplic_ip(vm):
    return vm['ip_addresses'][0]


def get_vm_2nd_puplic_ip(vm):
    return vm['ip_addresses'][1]


def get_vm_backup_policy(vm):
    return vm['backup_policy']
