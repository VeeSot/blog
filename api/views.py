from auth.views import UserAuth
from flask import jsonify, Blueprint, request
from main import app
from posts.models import Post, Comment

api = Blueprint('api', __name__)


class ApiPost():
    @staticmethod
    @app.route("/api/v1/posts/", methods=['GET'])
    def get_posts():
        """
        Return all post
        """
        posts_as_json = Post.get_json_with_field('title', 'img', 'slug', 'created_at')
        return jsonify({'posts': posts_as_json})


class ApiComment():
    @staticmethod
    @app.route("/api/v1/post/<post_title>/comment/<created_at>", methods=['PUT', 'DELETE'])
    def public_comment(post_title=None, created_at=None):
        """
        Make comment (un)visible for all
        Returns:
            json: Notify about current status comment
        """

        if UserAuth.is_admin() and not (post_title is None or created_at is None):
            if request.method == 'PUT':
                post = Post.objects.get(title=post_title)
                comment = Comment.get(post, created_at)
                comment.public = not comment.public  # Inverse current status
                post.save()
            elif request.method == 'DELETE':
                post = Post.objects.get(title=post_title)
                Comment.delete(post, created_at)
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'fail'})