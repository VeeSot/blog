import json

from auth.views import UserAuth
from flask import jsonify, Blueprint, request, Response
from main import app
from posts.models import Post, Comment

api = Blueprint('api', __name__, url_prefix='/api/v1')


class ApiPost:
    @staticmethod
    @api.route("/posts/", methods=['GET', 'POST', 'PATCH', 'DELETE'])
    @api.route("/posts/<title>", methods=['GET', 'POST', 'PATCH', 'DELETE'])
    def dispatcher_posts(title=None):
        if request.method == 'GET' and title is None:  # Пришел запрос на индекс
            return ApiPost.post_index()
        elif request.method == 'GET' and title:  # Нужен определеный пост
            return ApiPost.get_post(title)

    @classmethod
    def post_index(cls):
        """
        Return all post
        """
        response = Post.get_json_with_field('title', 'img', 'slug', 'created_at')
        return Response(json.dumps(response), mimetype='application/json')  # jsonify - don correct fot this case!

    @classmethod
    def get_post(cls, title):
        """
        Get specify post
        """
        post = Post.objects.get_or_404(title=title)

        public_comments = [{'body': comment.body,
                            'author': comment.author,
                            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')}
                           for comment in post.comments if comment.public]  # Комментарии разрешеные к публикации

        response = [{'title': post.title,
                     'slug': post.slug, 'img': post.img,
                     'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                     'body': post.body,
                     'comments': public_comments}]

        return Response(json.dumps(response), mimetype='application/json')


class ApiComment():
    @staticmethod
    @app.route("/comment/<created_at>", methods=['PUT', 'DELETE'])
    def change_comment(created_at=None):
        """
        Change comment make (un)visible or remove
        Returns:
            json: Notify about current status comment
        """

        if UserAuth.is_admin() and not (created_at is None):
            if request.method == 'PUT':
                Comment.change_public_status(created_at)
            elif request.method == 'DELETE':
                Comment.delete(created_at)
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'fail'})
