from functools import wraps

from flask.views import MethodView
from flask.ext.mongoengine.wtf import model_form
from flask import request, render_template, Blueprint, redirect, abort, session, make_response
from auth.models import User, SessionStorage
from mongoengine import DoesNotExist


auth = Blueprint('auth', __name__, template_folder='templates')


class UserAuth(MethodView):
    @staticmethod
    def get():
        form = model_form(User)(request.form)
        return render_template('auth/index.html', form=form)

    @staticmethod
    def post():
        if request.form:
            try:
                username = request.form['name']
                password = request.form['password']
                user = User.objects.get(name=username)
                if user and user.password == password:
                    # prepare response/redirect
                    response = make_response(redirect('/admin'))

                    if 'session' in request.cookies:
                        session_id = request.cookies['session']
                    else:
                        session_id = session['csrf_token']
                        # Setting user-cookie

                    response.set_cookie('session_id', value=session_id)

                    # After.We update our storage session(remove old + add new record)
                    record = SessionStorage()

                    record.remove_old_session(username)
                    record.user = username
                    record.session_key = session_id
                    record.save()

                    # And redirect to admin-panel
                    return response
                else:
                    raise DoesNotExist
            except DoesNotExist:
                return abort(401)

    @staticmethod
    def user_exist():
        if 'session_id' in request.cookies:
            session_id = request.cookies['session_id']
            return SessionStorage.objects.filter(session_key=session_id)
        else:
            return False


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not UserAuth.user_exist():
            return redirect('auth')
        return f(*args, **kwargs)

    return decorated


auth.add_url_rule('/auth/', view_func=UserAuth.as_view('auth'))