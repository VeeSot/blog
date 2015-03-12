from flask import Blueprint, render_template
from flask.views import MethodView


contacts = Blueprint('contacts', __name__, template_folder='templates')



class Contacts(MethodView):
    def get(self):
        return render_template('contacts/index.html')

# Register the urls
contacts.add_url_rule('/contacts/', view_func=Contacts.as_view('index'))