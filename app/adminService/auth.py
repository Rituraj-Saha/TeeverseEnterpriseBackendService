from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqladmin.authentication import AuthenticationBackend

from app.adminService.services.auth_proxy import verify_user_via_internal_api


class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.middlewares = []

    async def authenticate(self, request: Request):
        print("===> AdminAuth.authenticate() called")

        user_email = request.session.get("user_email")
        print("Session user_email:", user_email)

        if user_email:
            # Use internal API with dummy password (or skip password logic if you prefer)
            result = await verify_user_via_internal_api(user_email, "__session__")
            if result.get("success"):
                return result  # Returning email + role for sqladmin, customize if needed

        return False

    async def login(self, request: Request):
        print("===> AdminAuth.login() called")

        if request.method == "POST":
            form = await request.form()
            username = form.get("username")
            password = form.get("password")

            result = await verify_user_via_internal_api(username, password)

            if result.get("success"):
                request.session["user_email"] = result["email"]
                print("✅ Login success, redirecting to /admin")
                return RedirectResponse(url="/admin", status_code=303)

            print("❌ Login failed, redirecting to /admin/login")
            return RedirectResponse(url="/admin/login", status_code=303)

        return RedirectResponse(url="/admin/login", status_code=303)

    async def logout(self, request: Request):
        request.session.clear()
        return RedirectResponse(url="/admin/login", status_code=303)
