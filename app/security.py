from flask.ext.security import Security, SQLAlchemyUserDatastore

from .models import db, Role, User


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(datastore=user_datastore)
