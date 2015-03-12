from distutils import dirname
from main import blog
from os.path import abspath

from flask.ext.assets import Environment, Bundle

ROOT_PATH = dirname(dirname(abspath(__file__)))  # Main root dir
STATIC_ROOT = ROOT_PATH + '/static'

assets = Environment(blog)
# New setting for static files
assets.app.root_path = ROOT_PATH
assets.directory = STATIC_ROOT

# Sass support + convert into css
CSS_PATH = ROOT_PATH + '/static/css/'

ABS_IMG_PATH = '/static/img/'
REAL_IMG_PATH = ROOT_PATH + ABS_IMG_PATH
scss = Bundle(CSS_PATH + 'posts.scss', filters='pyscss', output='style.css')
assets.register('scss_all', scss)
