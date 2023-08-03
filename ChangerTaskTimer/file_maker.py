import jinja2
import os

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))  # place where jinja find template file


def placement(jinja_var: dict):
    """
    This func create a .timer file with help of jinja template
    """
    template = jinja_env.get_template('template.txt')  # template file

    filename = f"kns_{jinja_var['description'].lower()}.timer"
    if filename in os.listdir('files/'):
        return print(f"File with name timer_{jinja_var['description']} already exist")

    with open(f'files/{filename}', "w") as message:
        message.write(template.render(jinja_var))
        print(f"... wrote {filename}")
