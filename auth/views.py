import asjson
from flask.views import MethodView
from functools import wraps
from flask.ext.mongoengine.wtf import model_form
from flask import request, render_template, Blueprint, redirect, abort, session, make_response
from .models import User, SessionStorage
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
                    response = make_response(redirect('/panel_control'))

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
    def is_admin():
        # Выуживаем куки из различных мест,т.к. отправлять могут в виде атрибута  заголовков
        cookies = request.cookies
        if not cookies:  # Ничего не нашли на первой иттерации.Попробуем вытащить из заголовка
            try:
                cookies = asjson.loads(request.headers['Set-Cookie'])
            except KeyError:
                pass
        if 'session_id' in cookies:
            session_id = cookies['session_id']
            return bool(SessionStorage.objects.filter(session_key=session_id))
        else:
            return False


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not UserAuth.is_admin():
            return redirect('auth')
        return f(*args, **kwargs)

    return decorated


auth.add_url_rule('/auth/', view_func=UserAuth.as_view('auth'))
