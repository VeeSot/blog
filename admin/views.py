from flask import request, redirect, render_template, url_for, Blueprint
from flask.views import MethodView
from flask.ext.mongoengine.wtf import model_form
from main import app
import os
from main import ABS_IMG_PATH
from auth.views import requires_auth
from posts.models import Post, BlogPost
from tags.models import Tag
from werkzeug.utils import secure_filename

admin = Blueprint('admin', __name__, template_folder='templates')


def upload_file():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return ABS_IMG_PATH + filename


class List(MethodView):
    decorators = [requires_auth]
    cls = Post

    def get(self):
        posts = self.cls.objects.all()
        return render_template('admin/list.html', posts=posts)


class Detail(MethodView):
    decorators = [requires_auth]
    class_map = {
        'post': BlogPost,
    }

    def get_context(self, slug=None):
        if slug:
            post = Post.objects.get_or_404(slug=slug)
            # Handle old posts types as well
            cls = post.__class__ if post.__class__ != Post else BlogPost
            form_cls = model_form(cls, exclude=('created_at', 'comments', 'img'))
            if request.method == 'POST':
                form = form_cls(request.form, inital=post._data)
            else:
                form = form_cls(obj=post)
        else:
            # Determine which post type we need
            cls = self.class_map.get(request.args.get('type', 'post'))
            post = cls()
            form_cls = model_form(cls, exclude=('created_at', 'comments', 'img'))
            form = form_cls(request.form)
        context = {
            "post": post,
            "form": form,
            "create": slug is None
        }
        return context

    def get(self, slug):
        context = self.get_context(slug)
        return render_template('admin/detail.html', **context)

    def post(self, slug):
        context = self.get_context(slug)
        form = context.get('form')

        if form.validate():
            post = context.get('post')
            form.populate_obj(post)
            if request.files['file']:
                post.img = upload_file()
            post.save()

            return redirect(url_for('admin.index'))
        return render_template('admin/detail.html', **context)


class ListTags(MethodView):
    decorators = [requires_auth]

    def get(self):
        tags = Tag.objects.all()
        return render_template('admin/tags/list.html', tags=tags)


class DetailTag(MethodView):
    decorators = [requires_auth]

    def get_context(self, title=None):
        if title:
            tag = Tag.objects.get_or_404(title=title)
            cls = tag.__class__
            form_cls = model_form(cls)
            if request.method == 'POST':
                form = form_cls(request.form, inital=tag._data)
            else:
                form = form_cls(obj=tag)
        else:
            tag = Tag()
            form_cls = model_form(Tag)
            form = form_cls(request.form)
        context = {
            "tag": tag,
            "form": form,
            "create": title is None
        }
        return context

    def get(self, title):
        context = self.get_context(title)
        return render_template('admin/tags/detail.html', **context)

    def post(self, title):
        context = self.get_context(title)
        form = context.get('form')

        if form.validate():
            tag = context.get('tag')
            form.populate_obj(tag)
            tag.save()

            return redirect(url_for('admin.tags'))
        return render_template('admin/tags/detail.html', **context)


admin.add_url_rule('/panel_control/', view_func=List.as_view('index'))
admin.add_url_rule('/panel_control/create/', defaults={'slug': None}, view_func=Detail.as_view('create'))
admin.add_url_rule('/panel_control/<slug>/', view_func=Detail.as_view('edit'))

admin.add_url_rule('/panel_control/tags/', view_func=ListTags.as_view('tags'))
admin.add_url_rule('/panel_control/tags/create/', defaults={'tag_name': None},
                   view_func=DetailTag.as_view('create_tag'))
admin.add_url_rule('/panel_control/tags/<title>/', view_func=DetailTag.as_view('edit_tag'))