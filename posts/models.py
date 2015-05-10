from collections import namedtuple
from service.views import prepare_response
from tags.models import Tag

__author__ = 'veesot'

import datetime

from flask import url_for
from main import db, connection_db


class Post(db.DynamicDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    title = db.StringField(max_length=255, required=True)
    slug = db.StringField(max_length=255, required=True)
    comments = db.ListField(db.EmbeddedDocumentField('Comment'))
    tags = db.ListField(db.ObjectIdField('ObjectId'))

    def get_post_dict(self):
        """Представление в ввиде словаря.Может использоваться в JSON - ответе"""
        post_dict = prepare_response(self, ignore_fields=['id', 'email', 'comments'])  # We not need id and comments
        # Comment approve moderation
        return post_dict

    def get_absolute_url(self):
        return url_for('post', kwargs={"slug": self.slug})

    def __unicode__(self):
        return self.title

    @property
    def post_type(self):
        return self.__class__.__name__

    @classmethod
    def update_tags(cls, post, tags):
        post.tags = []

        for tag in tags:
            if Tag.objects.filter(title=tag):
                new_tag = Tag.objects.get(title=tag)
            else:
                new_tag = Tag(title=tag).save()

            post.tags.append(new_tag.id)

        post.save()

    @classmethod
    def get_title_tags(cls, post):
        """Return tags title from Tags"""
        tags = []
        tags_id = post.tags
        for tag_ig in tags_id:
            tags.append(Tag.objects.get(id=tag_ig).title)
        return tags

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'slug'],
        'ordering': ['-created_at']
    }


class Comment(db.EmbeddedDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    author = db.StringField(verbose_name="Ваше имя", max_length=255, required=True)
    email = db.EmailField(verbose_name="Ваш email(будет скрыт от просмотра,нужен для обратной связи с автором)")
    body = db.StringField(verbose_name="Комментарий", required=True)
    public = db.BooleanField(verbose_name="Опубликовать", default=False)

    @classmethod
    def get_meta_info_comment(cls, created_at):
        """"
        Args:
            post (Post): Post for comment
            created_at (str): timestamp created comment

        Returns:
            Comment: needed comment
        """
        # Timestamp in canonic view
        created_at = datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S.%f")

        # establish a connection to the database
        posts = connection_db.post
        meta_info_comment = posts.find_one({"comments.created_at": created_at}, {"_id": 0, 'title': 1, 'comments.$': 1})
        post = Post.objects.get(title=meta_info_comment['title'])

        for comment in post.comments:
            if comment.created_at == created_at:
                meta_info = namedtuple('meta_info_comment', 'post comment')
                meta_info_comment = meta_info(post, comment)
                return meta_info_comment

    @classmethod
    def delete(cls, created_at):
        """"
        Removing specified comment
        Args:
            created_at (str): timestamp created comment
        """
        meta_info_comment = cls.get_meta_info_comment(created_at)

        comment_for_remove = meta_info_comment.comment
        post = meta_info_comment.post

        comments = post.comments
        for comment in comments:
            if comment == comment_for_remove:
                comments.remove(comment)
                post.save()
                return

    @classmethod
    def change_public_status(cls, created_at):
        """"
        Public|un-public comment
        Args:
            created_at (str): timestamp created comment
        """

        meta_info_comment = cls.get_meta_info_comment(created_at)
        comment_for_change = meta_info_comment.comment
        post = meta_info_comment.post
        comments = post.comments
        for comment in comments:
            if comment == comment_for_change:
                comment.public = not comment.public  # Inverse current state
                post.save()
                return

    def __unicode__(self):
        return self.created_at


class BlogPost(Post):
    img = db.StringField(verbose_name="Изображение", default='')
    body = db.StringField(required=True)
