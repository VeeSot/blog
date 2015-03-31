from urllib.parse import urljoin
from flask import Blueprint
from flask.views import MethodView
from flask import request
from werkzeug.contrib.atom import AtomFeed
from posts.models import BlogPost


rss = Blueprint('rss', __name__, template_folder='templates')


def make_external(url):
    return urljoin(request.url_root, url)


class Rss(MethodView):
    def get(self):
        feed = AtomFeed('Записки программиста', feed_url=request.url, url=request.url_root)
        posts = BlogPost.objects.all()
        for post in posts:
            feed.add(post.title, post.slug,
                     content_type='html',
                     url=make_external('post/'+post.slug),
                     updated=post.created_at,
                     published=post.created_at)
        return feed.get_response()

# Register the urls
rss.add_url_rule('/rss/', view_func=Rss.as_view('index'))