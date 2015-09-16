from flask import Flask, render_template

from flask.ext.security import login_required
from flask.ext.admin.contrib import sqla

from app.admin import admin, UserAdmin, RoleAdmin, SecureAdminIndexView
from app.cart.controllers import cart
from app.models import db, migrate, User, Role
from app.security import user_datastore, security

import os


def create_app(config=None):
    app = Flask(__name__)

    if config is None:
        config = os.path.join(
            app.root_path, os.environ.get('FLASK_APPLICATION_SETTINGS'))

    app.config.from_pyfile(config)
    app.secret_key = app.config['SECRET_KEY']

    db.init_app(app)
    migrate.init_app(app, db)
    security.init_app(app, user_datastore)
    admin.init_app(app)

    admin.add_view(UserAdmin(User, db.session, category="Accounts"))
    admin.add_view(RoleAdmin(Role, db.session, category="Accounts"))

    app.register_blueprint(cart)

    @app.route('/')
    @login_required
    def index():
        return render_template('index.html')

    return app
