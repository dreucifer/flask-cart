from flask import Flask

from flask.ext.admin import helpers as admin_helpers

from app.admin import admin, UserAdmin, RoleAdmin
from app.cart.controllers import cart
from app.models import db, migrate, User, Role
from app.security import security

import os


def create_app(config=None):
    app = Flask(__name__)

    if config is None:
        config = os.path.join(
            app.root_path, os.environ.get('FLASK_APPLICATION_SETTINGS')
        )

    app.config.from_pyfile(config)
    app.secret_key = app.config['SECRET_KEY']

    db.init_app(app)
    migrate.init_app(app, db)
    sec_state = security.init_app(app)
    admin.init_app(app)

    admin.add_view(UserAdmin(User, db.session, category="Accounts"))
    admin.add_view(RoleAdmin(Role, db.session, category="Accounts"))

    @sec_state.context_processor
    def security_context_processor():
        return dict(
            admin_base_template=admin.base_template,
            admin_view=admin.index_view,
            h=admin_helpers,
        )

    app.register_blueprint(cart)

    return app
