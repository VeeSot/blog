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


class Admin(MethodView):
    decorators = [requires_auth]

    def get(self):
        return render_template('admin/base.html')


class PostList(MethodView):
    decorators = [requires_auth]
    cls = Post

    def get(self):
        posts = self.cls.objects.all()
        return render_template('admin/posts/list.html', posts=posts)


class PostDetail(MethodView):
    decorators = [requires_auth]
    class_map = {
        'post': BlogPost,
    }

    def get_context(self, slug=None):
        if slug:
            post = Post.objects.get_or_404(slug=slug)
            tags = post.tags
            # Handle old posts types as well
            cls = post.__class__ if post.__class__ != Post else BlogPost
            form_cls = model_form(cls, exclude=('created_at', 'comments', 'img', 'tags'))
            if request.method == 'POST':
                form = form_cls(request.form, inital=post._data)
            else:
                form = form_cls(obj=post)
        else:
            # Determine which post type we need
            cls = self.class_map.get(request.args.get('type', 'post'))
            post = cls()
            form_cls = model_form(cls, exclude=('created_at', 'comments', 'img', 'tags'))
            tags = {}
            form = form_cls(request.form)
        context = {
            "tags": tags,
            "post": post,
            "form": form,
            "create": slug is None
        }
        return context

    def get(self, slug):
        context = self.get_context(slug)
        return render_template('admin/posts/detail.html', **context)

    def post(self, slug):
        context = self.get_context(slug)
        form = context.get('form')

        if form.validate():
            post = context.get('post')
            form.populate_obj(post)
            file_exists = request.files['file']
            tags = request.form['tags']

            if file_exists:  # Attach image
                post.img = upload_file()

            post.save()

            tags_list = tags.split(" ")
            post.update_tags(tags_list)

            return redirect(url_for('admin.index'))
        return render_template('admin/posts/detail.html', **context)


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


admin.add_url_rule('/panel_control/', view_func=Admin.as_view('index'))

admin.add_url_rule('/panel_control/posts/', view_func=PostList.as_view('posts'))
admin.add_url_rule('/panel_control/post/create/', defaults={'slug': None}, view_func=PostDetail.as_view('post.create'))
admin.add_url_rule('/panel_control/post/<slug>/', view_func=PostDetail.as_view('post.update'))

admin.add_url_rule('/panel_control/tags/', view_func=ListTags.as_view('tags'))
admin.add_url_rule('/panel_control/tag/create/', defaults={'title': None}, view_func=DetailTag.as_view('tag.create'))
admin.add_url_rule('/panel_control/tag/<title>/', view_func=DetailTag.as_view('tag.update'))