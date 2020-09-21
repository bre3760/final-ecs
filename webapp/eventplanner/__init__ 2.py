# importing the flask class
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from eventplanner.config import Config
from flask_marshmallow import Marshmallow
from flask_httpauth import HTTPBasicAuth
from flask_user import roles_required
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect

# from flask.ext.httpauth import HTTPBasicAuth
# to create a relative db
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'  # function name of our route
login_manager.login_message_category = 'info'
ma = Marshmallow()
# for email i need an email server
auth = HTTPBasicAuth()

mail = Mail()
csrf = CSRFProtect()

# how to make a secure time token
# python
# from itsdangerous import TimedJSONWebSignature as Serializer
# s = Serializer('secret',30)
# token = s.dumps({'user_id':1}).decode('utf-8')
# s.loads(token)


def create_app(config_class=Config):
    app = Flask(__name__)  # as an instance
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    ma.init_app(app)
    csrf.init_app(app)

    from eventplanner.users.routes import users  # blueprint
    from eventplanner.events.routes import events  # blueprint
    from eventplanner.main.routes import main  # blueprint
    from eventplanner.errors.handlers import errors
    from eventplanner.payments.routes import payments
    from eventplanner.bookings.routes import bookings

    app.register_blueprint(users)
    app.register_blueprint(events)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(payments)
    app.register_blueprint(bookings)
    # for API blueprint
    # from eventplanner.api_1_0 import api as api_1_0_blueprint
    # app.register_blueprint(api_1_0_blueprint, url_prefix='/api/')
    from eventplanner.api_1_0.routes import api
    app.register_blueprint(api, url_prefix='/api/')

    return app
