from auth.views import UserAuth
from flask import Blueprint, request, redirect, render_template, url_for
import flask
from flask.views import MethodView
from flask.ext.mongoengine.wtf import model_form
from main import app
from .models import Post, Comment


posts = Blueprint('posts', __name__, template_folder='templates')


@app.route('/api/v1/comment/public', methods=["POST"])
def public_comment():
    """
    Make comment (un)visible for all
    Returns:
        json: Notify about current status comment
    """
    if UserAuth.is_admin() and 'created_at' in request.form and 'post_title' in request.form:
        post_title = request.form['post_title']
        created_at = request.form['created_at']
        post = Post.objects.get(title=post_title)
        comment = Comment.get(post, created_at)
        comment.public = not comment.public  # Inverse current status
        post.save()
        return flask.jsonify({'status': 'success'})
    else:
        return flask.jsonify({'status': 'fail'})


class ListView(MethodView):
    def get(self):
        posts = Post.objects.all()
        return render_template('posts/list.html', posts=posts)


class DetailView(MethodView):
    form = model_form(Comment, exclude=['created_at', 'public'])

    def get_context(self, slug):
        post = Post.objects.get_or_404(slug=slug)
        form = self.form(request.form)
        admin = UserAuth.is_admin()

        context = {
            "post": post,
            "form": form,
            "admin": admin
        }
        return context

    def get(self, slug):
        context = self.get_context(slug)
        return render_template('posts/detail.html', **context)

    def post(self, slug):
        context = self.get_context(slug)
        form = context.get('form')

        if form.validate():
            comment = Comment()
            form.populate_obj(comment)

            post = context.get('post')
            post.comments.append(comment)
            post.save()

            return redirect(url_for('posts.detail', slug=slug))
        return render_template('posts/detail.html', **context)


# Register the urls
posts.add_url_rule('/', view_func=ListView.as_view('list'))
posts.add_url_rule('/<slug>/', view_func=DetailView.as_view('detail'))
