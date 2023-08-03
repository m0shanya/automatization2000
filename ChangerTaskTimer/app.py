import os

from flask import Flask, request
from file_maker import placement
from objects import finder, line_finder, line_replace

app = Flask(__name__)


def check_filename(name: str) -> str:
    """
    This func checking the argument from url for the presence
    :param name: string
    :return: string
    """
    if ".timer" not in name:
        name += ".timer"
    return name


def obj():
    """
    This func returns dict where key is filename and value is file contents
    """
    files = os.listdir('files/')
    res_dct = {}

    for file in files:
        if ".timer" in file:
            res_dct[file] = finder(file)

    return res_dct


@app.route('/', methods=['GET'])
def query_records():
    """
    This method returns all .timer files like json object
    """
    app.logger.info(obj())  # console output
    return obj()


@app.route('/get/<filename>', methods=['GET'])
def some_record(filename):
    """
    This method returns concrete .timer file like json object
    """
    app.logger.info(finder(check_filename(filename)))
    return finder(check_filename(filename))


@app.route('/update/<filename>/', methods=['PATCH'])
def update_record(filename):
    """
    This method updates concrete .timer file and returns it like json object
    """
    filename = check_filename(filename)

    content = {'description': request.args.get('description'),  # populating a dictionary with query arguments
               'requires': request.args.get('requires'),
               'oncalendar': request.args.get('oncalendar'),
               'unit': request.args.get('unit'),
               'wantedby': request.args.get('wantedby')}

    res_dct = {}

    for key, value in content.items():  # forloop in content
        if content[key] is not None:
            res_dct[key] = value  # populating a dictionary with not nullable pairs(value != None)
        line_replace(line_finder(filename, res_dct), res_dct, filename)

    app.logger.info(finder(check_filename(filename)))
    return finder(check_filename(filename))


@app.route('/post/', methods=['POST'])
def create_record():
    """
    This method create new .timer file and returns all files like json object
    """
    content = {'description': request.args.get('description'),
               'requires': request.args.get('requires'),
               'oncalendar': request.args.get('oncalendar'),
               'unit': request.args.get('unit'),
               'wantedby': request.args.get('wantedby')}

    placement(content)

    app.logger.info(obj())

    return obj()


@app.route('/delete/<filename>', methods=['DELETE'])
def delete_record(filename):
    """
    This method deletes concrete .timer file and returns all files like json object
    """
    os.remove(f'files/{check_filename(filename)}')

    app.logger.info(obj())

    return obj()


if __name__ == "__main__":
    app.run(host="0.0.0.0")
