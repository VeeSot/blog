from os.path import dirname, abspath
import pymongo
from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.assets import Environment, Bundle
from third_party import COUNTERS


app = Flask(__name__)
ROOT_PATH = dirname(dirname(abspath(__file__)))  # Main root dir


# DB settings
app.config["MONGODB_SETTINGS"] = {'DB': "blog"}
app.config["SECRET_KEY"] = "secret_key"
db = MongoEngine(app)
# connection through pymogo for low-level request and actions(MongoEngine not capable of everything)
connection = pymongo.MongoClient()
connection_db = connection.blog


# Setting for static files
STATIC_ROOT = ROOT_PATH + '/static'
assets = Environment(app)
assets.app.root_path = ROOT_PATH
assets.directory = STATIC_ROOT
# Sass support + convert into css
SCSS_PATH = ROOT_PATH + '/static/scss/'
# Various scss
glob_css = Bundle(SCSS_PATH + 'global.scss', filters='pyscss', output='css/global.css')
hljs = Bundle(SCSS_PATH + 'hljs.scss', filters='pyscss', output='css/hljs.css')
posts = Bundle(SCSS_PATH + 'posts.scss', filters='pyscss', output='css/posts.css')
redactor = Bundle(SCSS_PATH + 'redactor.scss', filters='pyscss', output='css/redactor.css')
admin = Bundle(SCSS_PATH + 'admin.scss', filters='pyscss', output='css/admin.css')
# Reg for access from HTML-template
assets.register('glob_css', glob_css)
assets.register('hljs', hljs)
assets.register('posts', posts)
assets.register('redactor', redactor)
assets.register('admin', admin)
# Image setting(for upload image)
ABS_IMG_PATH = '/static/img/'
REAL_IMG_PATH = ROOT_PATH + ABS_IMG_PATH
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = REAL_IMG_PATH
app.config['COUNTERS'] = COUNTERS


def register_blueprints(app):
    # Prevents circular imports
    from posts.views import posts
    from admin.views import admin
    from about.views import about
    from contacts.views import contacts
    from rss.views import rss
    from auth.views import auth
    from api.views import api
    from service.views import service
    from tags.views import tags

    app.register_blueprint(contacts)
    app.register_blueprint(posts)
    app.register_blueprint(admin)
    app.register_blueprint(about)
    app.register_blueprint(rss)
    app.register_blueprint(auth)
    app.register_blueprint(api)
    app.register_blueprint(service)
    app.register_blueprint(tags)


register_blueprints(app)

if __name__ == '__main__':
    app.run()

# rewrites global setting from local param
try:
    from .local_settings import *
except ImportError:
    pass
