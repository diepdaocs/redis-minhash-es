def chunk_list(lst, size):
    lst_len = len(lst)
    for i in range(0, lst_len, size):
        yield lst[i: i + size]


def to_dict(obj, level=1, max_level=5):
    if level > max_level:
        return None
    if not hasattr(obj, "__dict__"):
        return obj
    result = {}
    for key, val in obj.__dict__.items():
        if key.startswith("_"):
            continue
        element = []
        if isinstance(val, list):
            for item in val:
                element.append(to_dict(item, level + 1, max_level))
        else:
            element = to_dict(val, level + 1, max_level)
        result[key] = element
    return result
