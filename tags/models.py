from collections import namedtuple
from main import db, connection_db


class Tag(db.DynamicDocument):
    title = db.StringField(max_length=50, required=True)

    def get_meta_info(self):
        """"
        Returns:
            meta info about tag: example post list with this tag
        """
        # Timestamp in canonic view
        # establish a connection to the database
        # Posts with tags
        posts_connection = connection_db.post
        posts = posts_connection.find({"tags": self.id}, {"_id": 0, 'title': 1})

        meta_info = namedtuple('meta_info_tag', 'posts')
        meta_info_tag = meta_info(posts)
        return meta_info_tag

    def __unicode__(self):
        return self.title
