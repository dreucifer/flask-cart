#!/usr/bin/env python
# encoding: utf-8
# manage.py

from flask import current_app

from flask.ext.script import Manager
from flask.ext.migrate import MigrateCommand

from app.models import db
from app.security import user_datastore
from app import create_app, models

manager = Manager(create_app)
manager.add_option('-c', '--config', dest='config', required=False)
manager.add_command('db', MigrateCommand)


@manager.shell
def make_shell_context():
    return dict(app=current_app, db=db, models=models)


@manager.command
def createdb():
    db.init_app(current_app)
    db.create_all()


@manager.command
def dropdb():
    db.init_app(current_app)
    db.drop_all()


@manager.command
def create_admin():
    admin_role = user_datastore.find_or_create_role(
        name='admin',
        description='Full Administrator Privliges'
    )

    admin_user = user_datastore.find_user(email='admin@example.com')
    if admin_user is None:
        admin_user = user_datastore.create_user(
            email='admin@example.com',
            password='admin'
        )

    user_datastore.add_role_to_user(admin_user, admin_role)

    db.session.commit()

if __name__ == '__main__':
    manager.run()
