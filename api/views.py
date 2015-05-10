import json

import asjson

from flask.ext.api import status
from mongoengine import ValidationError
from auth.views import UserAuth
from flask import jsonify, Blueprint, request, Response
from posts.models import Post, Comment
from service.views import prepare_response

api = Blueprint('api', __name__, url_prefix='/api/v1')


class ApiPost:
    @staticmethod
    @api.route("/posts/", methods=['GET', 'POST', 'PATCH', 'DELETE'])
    @api.route("/posts/<title>", methods=['GET', 'POST', 'PATCH', 'DELETE', 'PUT'])
    def dispatcher_posts(title=None):
        if request.method == 'GET' and title is None:  # Пришел запрос на индекс
            return ApiPost.index()
        elif request.method == 'GET' and title:  # Нужен определеный пост
            return ApiPost.get(title)
        elif request.method == 'POST' and request.data and title is None:  # Пришли данные для создания поста
            meta_info = json.loads(request.data.decode())
            return ApiPost.create(meta_info)
        elif request.method == 'PUT' and request.data and title:
            meta_info = json.loads(request.data.decode())
            return ApiPost.update(meta_info, title)
        elif request.method == 'DELETE' and title:
            return ApiPost.delete(title)

    @classmethod
    def index(cls):
        """
        Return all post
        """
        posts = Post.objects.all()
        response = []
        for post in posts:
            post_meta_info = post.get_post_dict()
            response.append(post_meta_info)
        return Response(asjson.dumps(response), mimetype='application/json')  # jsonify - don correct fot this case!

    @classmethod
    def get(cls, title):
        """
        Get specify post
        """
        post = Post.objects.get_or_404(title=title)
        response = post.get_post_dict()

        return jsonify(response)

    @classmethod
    def create(cls, meta_info):
        """
        Get specify post
        """
        try:
            post = Post(**meta_info)  # Create from meta_info dict
            post.save()
            response = prepare_response(post, ignore_fields=['id'])
        except ValidationError:
            response = []  # We ignored mistake on user-side.Temporary
        return Response(json.dumps(response), mimetype='application/json'), status.HTTP_201_CREATED

    @classmethod
    def update(cls, meta_info, title):
        """
        Update specify post
        """
        post = Post.objects.get(title=title)
        fields = meta_info.keys()
        for field in fields:
            post._data[field] = meta_info[field]
        post.save()
        response = post.get_post_dict()
        return jsonify(response)

    @classmethod
    def delete(cls, title):
        """
        Delete specify post
        """
        post = Post.objects.get(title=title)
        post.delete()
        response = []
        return Response(json.dumps(response), mimetype='application/json'), status.HTTP_204_NO_CONTENT


class ApiComment:
    @staticmethod
    @api.route("/posts/<title>/comments/", methods=['GET', 'POST'])
    def dispatcher_comments(title=None):
        post = Post.objects.get(title=title)
        if request.method == 'GET':  # Пришел запрос на список комментариев к посту.Отдаем только разрешеные
            return Response(asjson.dumps(post.get_public_comments()), mimetype='application/json')
        elif request.method == 'POST' and request.data:  # Пришли данные для добавления коммента
            meta_info = json.loads(request.data.decode())
            return post.add_comment(meta_info)

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

    @classmethod
    def index(cls):
        pass
