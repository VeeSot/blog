from main import db


class Tag(db.DynamicDocument):
    title = db.StringField(max_length=16, required=True)

    def __unicode__(self):
        return self.title
