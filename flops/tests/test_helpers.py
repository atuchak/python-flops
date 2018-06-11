import pytest

from flops.helpers import transform_dict_keys_to_underscore, transform_dict_keys_to_camelcase, order_list_by_dict_key

test_data = [
    [{'clientId': 123, 'client': 321}, {'client_id': 123, 'client': 321}],
    [{'testKey': [{'clientId': 123, 'client': 321}]}, {'test_key': [{'client_id': 123, 'client': 321}]}],
]


@pytest.mark.parametrize('in_dict, out_dict', test_data)
def test_transform_dict_keys_to_underscore(in_dict, out_dict):
    assert out_dict == transform_dict_keys_to_underscore(in_dict)


@pytest.mark.parametrize('out_dict, in_dict', test_data)
def test_transform_dict_keys_to_camelcase(in_dict, out_dict):
    assert out_dict == transform_dict_keys_to_camelcase(in_dict)


@pytest.mark.parametrize('unsorted_list, sorted_list', [
    ([{'k': 2}, {'k': 12}, {'k': 1}, {'b': 0}], [{'b': 0}, {'k': 1}, {'k': 2}, {'k': 12}]),
])
def test_order_list_by_dict_key(unsorted_list, sorted_list):
    assert sorted_list == order_list_by_dict_key(unsorted_list, key='k', descending=False)
