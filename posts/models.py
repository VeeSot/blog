__author__ = 'veesot'

import datetime

from flask import url_for
from main import db


class Post(db.DynamicDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    title = db.StringField(max_length=255, required=True)
    slug = db.StringField(max_length=255, required=True)
    comments = db.ListField(db.EmbeddedDocumentField('Comment'))

    def get_absolute_url(self):
        return url_for('post', kwargs={"slug": self.slug})

    def __unicode__(self):
        return self.title

    @property
    def post_type(self):
        return self.__class__.__name__

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created_at', 'slug'],
        'ordering': ['-created_at']
    }


class Comment(db.EmbeddedDocument):
    created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
    author = db.StringField(verbose_name="Ваше имя", max_length=255, required=True)
    email = db.EmailField(verbose_name="Ваше email(будет скрыт от просмотра,нужен для обратной связи с автором)")
    body = db.StringField(verbose_name="Комментарий", required=True)


class BlogPost(Post):
    img = db.StringField(verbose_name="Изображение", default='')
    body = db.StringField(required=True)
