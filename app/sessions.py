from datetime import datetime
from uuid import uuid4
from werkzeug.datastructures import CallbackDict
try:
    import cPickle as pickle
except ImportError:
    import pickle

from flask.sessions import SessionInterface, SessionMixin


class SQLAlchemySession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update=on_update)
        self.sid = sid
        self.modified = False


class ServerSessionInterface(SessionInterface):
    def _generate_sid(self):
        return unicode(uuid4())


class SQLAlchemySessionInterface(ServerSessionInterface):
    serializer = pickle
    session_class = SQLAlchemySession

    def __init__(self, app, db, model, key_prefix='session-'):
        if db is None:
            from flask.ext.sqlalchemy import SQLAlchemy
            db = SQLAlchemy(app)
        self.db = db
        self.key_prefix = key_prefix
        self.session_model = model

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self._generate_sid()
            return self.session_class(sid=sid)
        open_id = self.key_prefix + sid
        saved_session = self.session_model.query.filter_by(
            session_id=open_id).first()
        if saved_session and saved_session.expiry <= datetime.utcnow():
            self.db.session.delete(saved_session)
            self.db.session.commit()
        if saved_session:
            try:
                val = saved_session.data
                data = self.serializer.loads(str(val))
                return self.session_class(data, sid=sid)
            except:
                return self.session_class(sid=sid)
        return self.session_class(sid=sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        save_id = self.key_prefix + session.sid
        saved_session = self.session_model.query.filter_by(
            session_id=save_id).first()
        if not session:
            if saved_session:
                self.db.session.delete(saved_session)
                self.db.session.commit()
            response.delete_cookie(
                app.session_cookie_name,
                domain=domain,
                path=path
            )
            return

        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        expires = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        if saved_session:
            saved_session.data = val
            saved_session.expiry = expires
            self.db.session.commit()
        else:
            new_session = self.session_model(save_id, val, expires)
            self.db.session.add(new_session)
            self.db.session.commit()
        session_id = session.sid
        response.set_cookie(
            app.session_cookie_name,
            session_id,
            expires=expires,
            httponly=httponly,
            domain=domain,
            path=path,
            secure=secure
        )
