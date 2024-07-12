import json
import re


def diff(file1: str, file2: str) -> bool:
    """Checks two JMDL files for relevant differences.

    :param file1: The path to the first file.
    :type file1: str
    :param file2: The path to the second file.
    :type file2: str
    :return: True if the files are functionally identical, False otherwise.
    :rtype: bool
    """
    # Load the files
    json_data_1 = None
    with open(file1, "r") as file:
        json_data_1 = json.loads(file.read())
    json_data_2 = None
    with open(file2, "r") as file:
        json_data_2 = json.loads(file.read())
    # Check the version
    if json_data_1["version"] != json_data_2["version"]:
        raise ValueError(
            f"Version mismatch: {json_data_1['version']} != {json_data_2['version']}"
        )

    # Check Blocks
    diff1, diff2 = __dict_diff(
        json_data_1["/"]["blocks"],
        json_data_2["/"]["blocks"],
        ".*(description|layout|ports|V_min|V_max|VMagnitude).*",
    )
    return len(diff1) == 0 and len(diff2) == 0


def __dict_diff(
    dict1: dict, dict2: dict, ignore_result: str = "a{256}"
) -> tuple[dict, dict]:
    """Compares two dictionaries and returns the differences in two dictionaries.

    :param dict1: The first dictionary.
    :type dict1: dict
    :param dict2: The second dictionary.
    :type dict2: dict
    :param ignore_result: Ignore difference if the key matches this regex.
    :type ignore_result: str, default "a{256}"
    :return: A tuple of two dictionaries. The first dictionary contains the elements in dict1 but not dict2, the second one the other direction.
    :rtype: tuple[dict, dict]
    """
    filter_regex = re.compile(ignore_result)

    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        if isinstance(dict1, float) and isinstance(dict2, float):
            if abs(dict1 - dict2) < 0.0000001:
                return {}, {}
        if dict1 != dict2:
            return dict1, dict2
        return {}, {}
    diff1 = {}
    diff2 = {}
    for key in dict1:
        if key not in dict2:
            diff1[key] = dict1[key]
        else:
            _diff, _ = __dict_diff(dict1[key], dict2[key], ignore_result)
            if (not isinstance(_diff, dict) or len(_diff) > 0) and filter_regex.match(
                key
            ) is None:
                diff1[key] = _diff
    for key in dict2:
        if key not in dict1:
            diff2[key] = dict2[key]
        else:
            _, _diff = __dict_diff(dict1[key], dict2[key], ignore_result)
            if (not isinstance(_diff, dict) or len(_diff) > 0) and filter_regex.match(
                key
            ) is None:
                diff2[key] = _diff
    return diff1, diff2
