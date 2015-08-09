from operator import itemgetter
from flask import Blueprint, render_template
from flask.views import MethodView
from .models import Tag
from posts.models import Post

tags = Blueprint('tags', __name__, template_folder='templates')


class ListTag(MethodView):
    def get(self):
        tags = Tag.objects.all()
        return render_template('tags/list.html', tags=tags)


class DetailTag(MethodView):
    def get(self, title):
        # get documents with tag
        tag = Tag.objects.get_or_404(title=title)
        meta_info_tag = tag.get_meta_info()
        posts = []
        for post in meta_info_tag.posts:
            posts.append(Post.objects.get(title=post['title']))
        posts_by_time = sorted(posts, key=itemgetter('created_at'),reverse=True)
        return render_template('tags/detail.html', tag=tag, posts=posts_by_time)


# Register the urls
tags.add_url_rule('/tags/', view_func=ListTag.as_view('index'))
tags.add_url_rule('/tags/<title>/', view_func=DetailTag.as_view('detail'))
