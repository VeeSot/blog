import json

from auth.views import UserAuth
from flask import jsonify, Blueprint, request, Response
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
        return Response(json.dumps(posts_as_json), mimetype='application/json')  # jsonify - don correct fot this case!


class ApiComment():
    @staticmethod
    @app.route("/api/v1/comment/<created_at>", methods=['PUT', 'DELETE'])
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