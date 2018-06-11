import pytest

from flops.exceptions import NotFoundError
from flops.tests.helpers import generate_pub_keys, generate_pub_key


def test_add_pubkey(flops_client):
    pub_key = generate_pub_key(name_prefix='__test_add_pubkey')
    res = flops_client.add_pubkey(**pub_key)
    assert res
    assert 'id' in res
    pub_key['id'] = res['id']
    assert res['name'] == pub_key['name']
    assert res['public_key'] == pub_key['public_key']

    res = flops_client.get_pubkey(res['id'])
    assert res
    for key_name in ['id', 'name', 'public_key']:
        assert res[key_name] == pub_key[key_name]


def test_delete_pubkey(flops_client):
    pub_key = generate_pub_key(name_prefix='__test_add_pubkey')
    res = flops_client.add_pubkey(**pub_key)
    assert res
    pub_key_id = res['id']

    res_del = flops_client.delete_pubkey(pub_key_id)
    assert res_del
    assert res_del['status'] == 'OK'

    with pytest.raises(NotFoundError):
        flops_client.get_pubkey(pub_key_id)

    with pytest.raises(NotFoundError):
        flops_client.delete_pubkey(pub_key_id)


def test_get_pubkeys_by_name(flops_client):
    test_prefix = '__test_get_pubkeys_by_name'
    pub_keys = generate_pub_keys(name_prefix=test_prefix, num=2)

    pub_keys_id = []

    for pub_key in pub_keys:
        res = flops_client.add_pubkey(**pub_key)
        assert res
        pub_keys_id.append(res['id'])

    res = flops_client.get_pubkeys_by_name(test_prefix, match_type='startswith')
    assert res
    res_pub_keys_id = [p['id'] for p in res]

    for pub_key_id in pub_keys_id:
        assert pub_key_id in res_pub_keys_id


def test_edit_pubkey(flops_client):
    test_prefix = '__test_edit_pubkey'
    pub_key1, pub_key2 = generate_pub_keys(name_prefix=test_prefix, num=2)
    res_add = flops_client.add_pubkey(**pub_key1)
    assert res_add
    pub_key1_id = res_add['id']

    res_edit = flops_client.edit_pubkey(pub_key1_id, **pub_key2)
    assert res_edit
    assert res_edit['id'] == pub_key1_id
    assert res_edit['name'] == pub_key2['name']
    assert res_edit['public_key'] == pub_key2['public_key']
