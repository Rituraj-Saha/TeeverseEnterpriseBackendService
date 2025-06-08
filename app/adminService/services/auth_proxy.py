import httpx
from app.config import settings

async def verify_user_via_internal_api(email: str, password: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.INTERNAL_API_URL}/internal/verify-user",
            json={"email": email, "password": password},
            # params={"email": email, "password": password},
            headers={"x-internal-token": settings.INTERNAL_SECRET_TOKEN}
        )
        response.raise_for_status()
        return response.json()
