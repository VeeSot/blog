from flask import send_from_directory, request, make_response, Blueprint
from jinja2 import Environment, FileSystemLoader
from main import STATIC_ROOT, ROOT_PATH, app
import os
from posts.models import BlogPost

service = Blueprint('service', __name__, template_folder='templates')


@app.route('/robots.txt')
def robots():
    return send_from_directory(STATIC_ROOT, request.path[1:])


@app.route("/sitemap.xml", methods=["GET"])
def sitemap():
    """Generate sitemap.xml"""
    posts = BlogPost.objects.all()
    # Configure jinja for internal templates
    env = Environment(autoescape=True, extensions=['jinja2.ext.i18n'],
                      loader=FileSystemLoader(os.path.join(ROOT_PATH, 'templates')))
    url_root = request.url_root[:-1]
    sitemap_xml = env.get_template("sitemap_template.xml").render(
        posts=posts, url_root=url_root)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response

