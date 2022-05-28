import os
import imp
from flask import Flask

import secrets

# Create app variable, init creates a module which can be imported
app = Flask(__name__)
db = None

config = imp.load_source('*', os.path.realpath('config.py'))
app.config.from_object(config)


from app.db import db

db.init_app(app)
with app.app_context():
    db.create_all()

from app.controller.artifacts import artifacts_api
app.register_blueprint(artifacts_api)


secret = secrets.token_urlsafe(32)

app.secret_key = secret
# def init_app():

   

#     #initialize db
#     return app 




# if __name__ == "__main__":
#     init_app().run()




