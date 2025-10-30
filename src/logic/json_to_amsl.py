import yaml


def json_to_amsl(json_data: str) -> str:
    """
    Convert JSON data to YAML format.
    Removes the importance field from each topic.

    Args:
        json_data: JSON data to convert
    Returns:
        YAML formatted string
    """
    json_dict = yaml.safe_load(json_data)
    # Drop importance scores if present
    for item in json_dict:
        if "importance" in item:
            del item["importance"]
    yaml_data = yaml.safe_dump(json_dict, sort_keys=False)
    return yaml_data
