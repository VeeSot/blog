from flask import Blueprint, render_template
from flask.views import MethodView


about = Blueprint('about', __name__, template_folder='templates')


class About(MethodView):
    @staticmethod
    def get():
        return render_template('about/index.html')

# Register the urls
about.add_url_rule('/about/', view_func=About.as_view('index'))