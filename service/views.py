from flask import send_from_directory, request, make_response, Blueprint
from jinja2 import Environment, FileSystemLoader
from main import STATIC_ROOT, ROOT_PATH, app
import os

service = Blueprint('service', __name__, template_folder='templates')


@app.route('/robots.txt')
def robots():
    return send_from_directory(STATIC_ROOT, request.path[1:])


@app.route("/sitemap.xml", methods=["GET"])
def sitemap():
    """Generate sitemap.xml"""
    from posts.models import BlogPost

    posts = BlogPost.objects.filter(public=True)
    # Configure jinja for internal templates
    env = Environment(autoescape=True, extensions=['jinja2.ext.i18n'],
                      loader=FileSystemLoader(os.path.join(ROOT_PATH, 'templates')))
    url_root = request.url_root[:-1]
    sitemap_xml = env.get_template("sitemap_template.xml").render(
        posts=posts, url_root=url_root)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response


def prepare_response(model, ignore_fields=None):
    """Create dict specify model"""
    response = {}
    for attribute in model:
        if attribute not in ignore_fields:
            if isinstance(model._data[attribute], list):
                # List may include other element.Use recursion
                included_list = []
                for element in model._data[attribute]:
                    included_list.append(prepare_response(element, ignore_fields))
                response[attribute] = included_list
            else:
                response[attribute] = model._data[attribute]
    return response


def instance_to_dict(model, *args):
    """""
    Конвертирует Flask-вскую Model в обычный словарик.
    Аргументами принимает поля по которым делается выбрка из Model
    """""
    model_dict = {}
    for arg in args:
        try:
            value = getattr(model, arg)
        except:  # Возможны неприятности с преобразованиями
            value = ''
        model_dict[arg] = value
        # Переобразовываем в строковое представление при надобности
    return model_dict
