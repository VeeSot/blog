from flask import Flask
from flask.ext.mongoengine import MongoEngine


blog = Flask(__name__)

# DB settings

blog.config["MONGODB_SETTINGS"] = {'DB': "blog"}
blog.config["SECRET_KEY"] = "9885c535484942f17e08370161a108b0"
db = MongoEngine(blog)


def register_blueprints(blog):
    # Prevents circular imports
    from posts.views import posts
    from admin.views import admin
    from about.views import about
    from contacts.views import contacts
    from rss.views import rss
    from auth.views import auth

    blog.register_blueprint(contacts)
    blog.register_blueprint(posts)
    blog.register_blueprint(admin)
    blog.register_blueprint(about)
    blog.register_blueprint(rss)
    blog.register_blueprint(auth)


register_blueprints(blog)

if __name__ == '__main__':
    blog.run()