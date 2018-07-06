import json


def read_json(path):
    """
    Read and load the json data from the provided path.

    :param str path:
    :return: Json data
    """
    with open(path) as f:
        data = json.load(f)
        
    return data
