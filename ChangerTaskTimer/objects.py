import configparser
import json


def finder(filename):
    """
    This func create a json object from .timer file
    """
    path = filename

    config_object = configparser.ConfigParser()
    file = open(f'files/{path}', "r")
    config_object.read_file(file)
    output_dict = {}
    sections = config_object.sections()

    for section in sections:
        items = config_object.items(section)
        output_dict[section] = dict(items)

    file.close()
    return output_dict


def line_finder(filename, replacement: dict) -> dict:
    """
    This func finding the old data which have entries with detected arguments from request
    """
    content = finder(filename)
    old_data = {}

    for key in content.keys():
        for k in content[key].keys():
            if k in replacement.keys():
                old_data[k] = content[key][k]

    return old_data


def line_replace(old_value: dict, new_value: dict, filename: str):
    """
    This func replace old data to the newest in json obj and calls the converter to .timer
    """
    element_to_parse = finder(filename)

    for key in element_to_parse.keys():
        for k in element_to_parse[key].keys():
            if k in old_value.keys():
                element_to_parse[key][k] = new_value[k]

    convert_to_txt(element_to_parse, filename)


def convert_to_txt(content: dict, filename: str):
    """
    converter from json to timer
    """
    path = filename

    element = json.dumps(content)

    file = open(f'files/{path}', "w")
    python_dict = json.loads(element)
    config_object = configparser.ConfigParser()
    sections = python_dict.keys()
    for section in sections:
        config_object.add_section(section)
    for section in sections:
        inner_dict = python_dict[section]
        fields = inner_dict.keys()
        for field in fields:
            value = inner_dict[field]
            config_object.set(section, field, str(value))
    config_object.write(file)
    file.close()
