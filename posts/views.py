from auth.views import UserAuth
from flask import Blueprint, request, redirect, render_template, url_for, flash
from flask.views import MethodView
from flask.ext.mongoengine.wtf import model_form
from .models import Post, Comment

posts = Blueprint('posts', __name__, template_folder='templates')


class Posts(MethodView):
    def get(self):
        return render_template('index.html')


class PostList(MethodView):
    def get(self):
        posts = Post.objects.filter(public=True)  # Only public posts, no draft
        return render_template('posts/list.html', posts=posts)


class PostDetail(MethodView):
    form = model_form(Comment, exclude=['created_at', 'public'])

    def get_context(self, slug):
        post = Post.objects.get_or_404(slug=slug)
        form = self.form(request.form)
        admin = UserAuth.is_admin()
        tags = Post.get_title_tags(post)

        context = {
            "tags": tags,
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
            flash('Thank you for your comment.It will be published after checking')

            return redirect(url_for('posts.detail', slug=slug))
        return render_template('posts/detail.html', **context)

# Register the urls
posts.add_url_rule('/', view_func=PostList.as_view('list'))
posts.add_url_rule('/posts', view_func=Posts.as_view('posts'))
posts.add_url_rule('/post/<slug>/', view_func=PostDetail.as_view('detail'))
