from starlette.requests import Request
from starlette.responses import RedirectResponse
from app.authService.services.auth import get_user_by_email, verify_password
from app.database import SessionLocal
from sqladmin.authentication import AuthenticationBackend


class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.middlewares = []

    async def authenticate(self, request: Request):
        print("===> AdminAuth.authenticate() called")
        print("Request method:", request.method)

        user_email = request.session.get("user_email")
        print("Session user_email:", user_email)

        if user_email:
            async with SessionLocal() as db:
                user = await get_user_by_email(db, user_email)
                if user and user.role == "admin":
                    return user
        return False

    async def login(self, request: Request):
        print("===> AdminAuth.login() called")
        if request.method == "POST":
            form = await request.form()
            username = form.get("username")
            password = form.get("password")

            async with SessionLocal() as db:
                user = await get_user_by_email(db, username)
                if user:
                    password_valid = await verify_password(password, user.password)
                    if password_valid and user.role == "admin":
                        request.session["user_email"] = user.email
                        print("✅ Login success, redirecting to /admin")
                        return RedirectResponse(url="/admin", status_code=303)

            print("❌ Login failed, redirecting to /admin/login")
            return RedirectResponse(url="/admin/login", status_code=303)

        # Default to showing login page
        return RedirectResponse(url="/admin/login", status_code=303)

    async def logout(self, request: Request):
        request.session.clear()
        return RedirectResponse(url="/admin/login", status_code=303)
