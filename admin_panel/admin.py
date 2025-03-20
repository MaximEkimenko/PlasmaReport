"""Настройка панели администратора."""
from fastapi import FastAPI
from sqladmin import Admin, ModelView

from auth.models import User
from db.database import engine
from techman.models import FioDoer
from admin_panel.admin_auth import authentication_backend


class UserAdmin(ModelView, model=User):
    """Настройки модели User в панели администратора."""

    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True
    page_size = 100
    column_exclude_list = (User.hashed_password, )
    column_details_exclude_list = (User.hashed_password, )


class FioDoerAdmin(ModelView, model=FioDoer):
    """Настройки модели User в панели администратора."""

    column_list = (FioDoer.fio_doer, FioDoer.user_id, FioDoer.id, FioDoer.position)
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


def create_admin_panel(app: FastAPI) -> Admin:
    """Подключение панели администратора к приложению."""
    admin = Admin(app, engine, authentication_backend=authentication_backend)
    admin.add_view(FioDoerAdmin)
    admin.add_view(UserAdmin)

    return admin

