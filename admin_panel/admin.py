"""Настройка панели администратора."""
from fastapi import FastAPI
from sqladmin import Admin, ModelView

from auth.models import User
from db.database import engine
from admin_panel.admin_auth import authentication_backend


class UserAdmin(ModelView, model=User):
    """Настройки модели User в панели администратора."""

    all_fields_list = (User.id, User.first_name, User.last_name, User.email, User.role)
    column_list = all_fields_list
    column_searchable_list = all_fields_list
    column_sortable_list = all_fields_list
    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True
    page_size = 100
    column_details_exclude_list = (User.password, )


def create_admin_panel(app: FastAPI) -> Admin:
    """Подключение панели администратора к приложению."""
    admin = Admin(app, engine, authentication_backend=authentication_backend)
    admin.add_view(UserAdmin)
    return admin

