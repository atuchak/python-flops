def underscore_to_camelcase(value):
    def camelcase():
        yield str.lower
        while True:
            yield str.capitalize

    c = camelcase()
    return ''.join(next(c)(x) if x else '_' for x in value.split('_'))


def camelcase_to_underscore(value):
    def camelcase(char):
        if char.isupper():
            return '_' + char.lower()
        else:
            return char.lower()

    return ''.join(camelcase(v) for v in value)


def transform_dict_keys_to_camelcase(data):
    if isinstance(data, dict):
        return {underscore_to_camelcase(k): transform_dict_keys_to_camelcase(v) for k, v in data.items()}
    if isinstance(data, list):
        return [transform_dict_keys_to_camelcase(v) for v in data]
    return data


def transform_dict_keys_to_underscore(data):
    if isinstance(data, dict):
        return {camelcase_to_underscore(k): transform_dict_keys_to_underscore(v) for k, v in data.items()}
    if isinstance(data, list):
        return [transform_dict_keys_to_underscore(v) for v in data]
    return data


def order_list_by_dict_key(data, key, descending=False):
    default_value = 0
    return sorted(data, key=lambda k: k.get(key, default_value), reverse=descending)
