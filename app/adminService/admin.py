from sqladmin import Admin, ModelView
from app.databaseConfigs.models.authServiceModel.user import User
from app.databaseConfigs.database import engine
from app.adminService.auth import AdminAuth


class UserAdmin(ModelView, model=User):
    column_list = [User.userid, User.email, User.role,User.address,User.name]
    column_searchable_list = [User.email,User.phone_number,User.name]
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

admin_auth = AdminAuth(secret_key="supersecretkey")  # can reuse JWT secret

def setup_admin(app):
    admin = Admin(app, engine, authentication_backend=admin_auth)
    admin.add_view(UserAdmin)
