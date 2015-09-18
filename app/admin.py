from flask import abort, redirect, url_for, request

from flask.ext.admin import Admin, AdminIndexView, expose
from flask.ext.admin.contrib import sqla
from flask.ext.security import current_user

from wtforms.fields import PasswordField

class AdminMixin(object):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if current_user.has_role('admin'):
            return True
        return False

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('security.login', next=request.url))


class SecureAdminIndexView(AdminMixin, AdminIndexView):
    @expose('/')
    def index(self):
        return super(SecureAdminIndexView, self).index()


class UserAdmin(AdminMixin, sqla.ModelView):
    column_exclude_list = ('password',)
    form_exclude_list = ('password',)
    column_auto_select_related = True

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('security.login', next=request.url))

    def scaffold_form(self):
        form_class = super(UserAdmin, self).scaffold_form()
        form_class.password = PasswordField('New Password')
        return form_class


class RoleAdmin(AdminMixin, sqla.ModelView):
    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)
            else:
                return redirect(url_for('security.login', next=request.url))

admin = Admin(
    base_template='my_master.html',
    index_view=SecureAdminIndexView(),
    template_mode='bootstrap3',
)
