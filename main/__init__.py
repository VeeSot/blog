from os.path import dirname, abspath
from flask import Flask
from flask.ext.mongoengine import MongoEngine
from flask.ext.assets import Environment, Bundle


app = Flask(__name__)
ROOT_PATH = dirname(dirname(abspath(__file__)))  # Main root dir
# DB settings
app.config["MONGODB_SETTINGS"] = {'DB': "blog"}
app.config["SECRET_KEY"] = "9885c535484942f17e08370161a108b0"
db = MongoEngine(app)
# Setting for static files
STATIC_ROOT = ROOT_PATH + '/static'
assets = Environment(app)
assets.app.root_path = ROOT_PATH
assets.directory = STATIC_ROOT
# Sass support + convert into css
CSS_PATH = ROOT_PATH + '/static/css/'
scss = Bundle(CSS_PATH + 'posts.scss', filters='pyscss', output='style.css')
assets.register('scss_all', scss)
# Image setting(for upload image)
ABS_IMG_PATH = '/static/img/'
REAL_IMG_PATH = ROOT_PATH + ABS_IMG_PATH
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = REAL_IMG_PATH


def register_blueprints(app):
    # Prevents circular imports
    from posts.views import posts
    from admin.views import admin
    from about.views import about
    from contacts.views import contacts
    from rss.views import rss
    from auth.views import auth

    app.register_blueprint(contacts)
    app.register_blueprint(posts)
    app.register_blueprint(admin)
    app.register_blueprint(about)
    app.register_blueprint(rss)
    app.register_blueprint(auth)


register_blueprints(app)

if __name__ == '__main__':
    app.run()

# rewrites global setting from local param
try:
    from .local_setting import *
except ImportError:
    pass
