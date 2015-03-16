from flask import Flask
from flask.ext.mongoengine import MongoEngine


app = Flask(__name__)

# DB settings

app.config["MONGODB_SETTINGS"] = {'DB': "blog"}
app.config["SECRET_KEY"] = "9885c535484942f17e08370161a108b0"
db = MongoEngine(app)


def register_blueprints(app):
    # Prevents circular imports
    from posts.views import posts
    from admin.views import admin
    from about.views import about
    from contacts.views import contacts
    from rss.views import rss
    from auth.views import auth

    app.register_blueprint(contacts)
    app.register_blueprint(posts)
    app.register_blueprint(admin)
    app.register_blueprint(about)
    app.register_blueprint(rss)
    app.register_blueprint(auth)


register_blueprints(app)

if __name__ == '__main__':
    app.run()