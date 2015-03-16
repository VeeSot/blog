from main import db


class User(db.DynamicDocument):
    name = db.StringField(max_length=32, required=True)
    password = db.StringField(max_length=32, required=True)

    def __unicode__(self):
        return self.name


class SessionStorage(db.DynamicDocument):
    user = db.StringField(max_length=32, required=True)
    session_key = db.StringField(max_length=111, required=True)

    @classmethod
    def remove_old_session(cls, username):
        # We remove all old session for  and freed space
        records = cls.objects.filter(user=username)
        for record in records:
            record.delete()