import datetime

import operator
import asjson
from flask.ext.api import status
from mongoengine import ValidationError, DoesNotExist
from auth.views import UserAuth
from flask import Blueprint, request, Response
from posts.models import BlogPost, Comment
import random
from tags.models import Tag as post_tags
from werkzeug.exceptions import Forbidden

class_post = BlogPost.__base__.__name__.lower()

api = Blueprint('api', __name__, url_prefix='/api/v1')


class Api:
    @classmethod
    def handler_201(cls, resource, title):
        return {"code": 201, "messages": "{0} with title {1} been created".format(resource, title)}

    @classmethod
    def handler_404(cls, resource, title):
        return {"code": 404, "messages": "{0} with title '{1}' not found".format(resource, title)}

    @classmethod
    def handler_403(cls, resource):
        return {"code": 403, "messages": "Access to {0} forbidden".format(resource)}

    @classmethod
    def handler_400(cls, metadata, resource):
        return {"code": 400, "messages": "Data {0} for {1} not for passed validation".format(metadata, resource)}

    @classmethod
    def handler_500(cls, error):
        return {"code": 500, "messages": "Server response '{0}'.Correct you request and retry".format(error)}

    @classmethod
    def handler_204(cls, resource, title):
        return {"code": 204, "messages": "'{0}' with name {1) been removed".format(resource, title)}


class Post(Api):
    @staticmethod
    @api.route("/posts/", methods=['GET', 'POST'])
    @api.route("/posts/<title>", methods=['GET', 'POST', 'PATCH', 'DELETE', 'PUT'])
    def dispatcher_posts(title=None):
        try:
            if request.method == 'GET':
                # Разбор дополнительных GET-параметров
                partial_content = None  # По умолчанию мы считаем что пользователю не нужнен частичный ответ
                if request.query_string and b'fields' in request.query_string:
                    partial_content = request.args['fields'].split(',')  # Собираем список важных атрибутов

                if title is None:  # Пришел запрос на индекс
                    return Post.index(partial_content)
                elif title:  # Нужен определеный пост
                    return Post.get(title, partial_content)
            elif request.method == 'POST' and request.data and title is None:  # Пришли данные для создания поста
                meta_info = asjson.loads(request.data.decode())
                return Post.create(meta_info)
            elif request.method == 'PUT' or request.method == 'PATCH' and request.data and title:
                meta_info = asjson.loads(request.data.decode())
                return Post.update(meta_info, title)
            elif request.method == 'DELETE' and title:
                return Post.delete(title)
        except ValueError as error:  # Один обработчик на косячный ввод данных(наличие нужны/отсутствие важных символов)
            response = Api.handler_500(error)
            code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response(asjson.dumps(response), mimetype='application/json'), code

    @classmethod
    def index(cls, partial_content, order_by=None, offset=0, limit=10):
        """
        Return post list by criteria
        """
        if request.query_string:  # Проверка дополнительных входных параметров
            if 'orderBy' in request.args:
                order_by = request.args['orderBy'].split(',')  # Собираем атрибутов для сортировки
            # Параметры для паджинации
            if 'offset' in request.args:
                offset = int(request.args['offset'])
            if 'limit' in request.args:
                limit = int(request.args['limit'])

        posts = list(BlogPost.objects.filter(public=True).limit(limit).skip(offset))
        if order_by:
            posts.sort(key=operator.attrgetter(*order_by))

        response = []
        for post in posts:
            post_meta_info = post.get_post_dict(partial_content)
            response.append(post_meta_info)
        return Response(asjson.dumps(response), mimetype='application/json')  # jsonify - don correct fot this case!

    @classmethod
    def get(cls, title, partial_content):
        """
        Get specify post
        """
        try:
            post = BlogPost.objects.get(title=title)
            if post.public:  # Если пост допущен к публикации.
                response = post.get_post_dict(partial_content)
                code = status.HTTP_200_OK
            else:  # Если запрашивают неопубликованый,но существующий пост
                response = Api.handler_403(class_post)
                code = status.HTTP_403_FORBIDDEN
        except DoesNotExist:
            response = Api.handler_404(class_post, title)
            code = status.HTTP_404_NOT_FOUND
        return Response(asjson.dumps(response), mimetype='application/json'), code

    @classmethod
    def create(cls, metadata):
        """
        Create new post
        """
        try:
            if not UserAuth.is_admin():
                raise Forbidden
            post = BlogPost(**metadata)  # Create from meta_info dict
            post.save()
            response = post.get_post_dict()
            code = status.HTTP_201_CREATED
        except ValidationError:
            response = Api.handler_400(metadata, class_post)
            code = status.HTTP_400_BAD_REQUEST
        except Forbidden:
            response = Api.handler_403(class_post)
            code = status.HTTP_403_FORBIDDEN

        return Response(asjson.dumps(response), mimetype='application/json'), code

    @classmethod
    def update(cls, meta_info, title):
        """
        Update specify post
        """
        try:
            if not UserAuth.is_admin():
                raise Forbidden
            post = BlogPost.objects.get(title=title)
            fields = meta_info.keys()
            for field in fields:
                if field in post:  # Если атрибут совместим с моделью и нам не прислали фигню.Недостатки schema-less
                    setattr(post, field, meta_info[field])
                else:
                    raise ValidationError
            post.save()
            response = post.get_post_dict()
            code = status.HTTP_200_OK
        except DoesNotExist:
            response = Api.handler_404(class_post, title)
            code = status.HTTP_404_NOT_FOUND
        except Forbidden:
            response = Api.handler_403(class_post)
            code = status.HTTP_403_FORBIDDEN
        except ValidationError:
            response = Api.handler_400(meta_info, class_post)
            code = status.HTTP_400_BAD_REQUEST
        return Response(asjson.dumps(response), mimetype='application/json'), code

    @classmethod
    def delete(cls, title):
        """
        Delete specify post
        """
        try:
            if not UserAuth.is_admin():
                raise Forbidden
            post = BlogPost.objects.get(title=title)
            post.delete()
            response = Api.handler_204(class_post, title)
            code = status.HTTP_204_NO_CONTENT
        except DoesNotExist:
            response = Api.handler_404(class_post, title)
            code = status.HTTP_404_NOT_FOUND
        except Forbidden:
            response = Api.handler_403(class_post)
            code = status.HTTP_403_FORBIDDEN
        return Response(asjson.dumps(response), mimetype='application/json'), code


class ApiComment:
    @staticmethod
    @api.route("/posts/<title>/comments/", methods=['GET', 'POST'])
    @api.route("/posts/<title>/comments/<created_at>", methods=['PATCH', 'DELETE'])
    def dispatcher_comments(title=None, created_at=None):
        post = BlogPost.objects.get(title=title)
        if request.method == 'GET':  # Пришел запрос на список комментариев к посту.Отдаем только разрешеные
            return Response(asjson.dumps(post.get_comments(public=True)), mimetype='application/json')
        elif request.method == 'POST' and request.data:  # Пришли данные для добавления коммента
            meta_info = asjson.loads(request.data.decode())
            return asjson.dumps(post.add_comment(meta_info))
        elif request.method == 'PATCH' and created_at:
            return ApiComment.update(post, created_at)
        elif request.method == 'DELETE' and created_at:
            return ApiComment.delete(post, created_at)

    @classmethod
    def update(cls, post, created_at):
        """
        Change comment make (un)visible or remove
        Returns:
            json: Notify about current status comment
        """

        if UserAuth.is_admin() and created_at:
            created_at = datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%f")
            comment = Comment.change_public_status(post, created_at)
            response = comment.get_comment_dict()
            return Response(asjson.dumps(response), mimetype='application/json')
        else:
            return Response(asjson.dumps([]), mimetype='application/json'), status.HTTP_403_FORBIDDEN

    @classmethod
    def delete(cls, post, created_at):
        """
        Change comment make (un)visible or remove
        Returns:
            json: Notify about current status comment
        """
        response = []
        if UserAuth.is_admin() and created_at:
            created_at = datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%f")
            Comment.delete(post, created_at)
            return Response(asjson.dumps(response), mimetype='application/json'), status.HTTP_204_NO_CONTENT
        else:
            return Response(asjson.dumps(response), mimetype='application/json'), status.HTTP_403_FORBIDDEN


class Tag(Api):
    @staticmethod
    @api.route("/tags/", methods=['GET'])
    def dispatcher_tags(title=None):
        try:
            if title is None:
                return Tag.index()
        except ValueError as error:
            response = Api.handler_500(error)
            code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response(asjson.dumps(response), mimetype='application/json'), code

    @classmethod
    def index(cls, count=None, random_order=False):
        """
        Return tags list
        """
        if request.query_string:
            # Проверки входных данных
            if 'count' in request.args and request.args['count'].isdigit():
                count = int(request.args['count'])
            if 'random_order' in request.args and request.args['random_order'] == 'true':
                random_order = True

        tags = list(post_tags.objects.all())

        if random_order and count < len(tags):
            # Если нам нужен "случайный" набор тегов и  тегов запросили меньше чем есть - перемешаем их
            random.shuffle(tags)
            tags = tags[:count]  # Усечение списка тегов

        response = []
        for tag in tags:
            tag_meta_info = tag.get_tag_dict()
            response.append(tag_meta_info)
        return Response(asjson.dumps(response), mimetype='application/json')  # jsonify - don correct fot this case!
