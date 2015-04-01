from collections import namedtuple
import pymongo
from main import db


class Tag(db.DynamicDocument):
    title = db.StringField(max_length=50, required=True)

    def get_meta_info(self):
        """"
        Returns:
            meta info about tag: example post list with this tag
        """
        # Timestamp in canonic view
        title = self.title

        # establish a connection to the database
        connection = pymongo.MongoClient("mongodb://localhost")

        # Posts with tags
        posts_connection = connection.blog.post
        posts = posts_connection.find({"tags.title": title}, {"_id": 0, 'title': 1})

        meta_info = namedtuple('meta_info_tag', 'posts')
        meta_info_tag = meta_info(posts)
        return meta_info_tag

    def __unicode__(self):
        return self.title
