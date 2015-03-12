from flask import Blueprint, render_template
from flask.views import MethodView


rss = Blueprint('rss', __name__, template_folder='templates')



class Rss(MethodView):
    def get(self):
        return render_template('rss/index.html')

# Register the urls
rss.add_url_rule('/rss/', view_func=Rss.as_view('index'))