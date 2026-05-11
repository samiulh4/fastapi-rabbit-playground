from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.database import user_collection

router = APIRouter(prefix="/users", tags=["users"])

@router.get('/online')
async def get_online_users():
    cursor = user_collection.find({"is_online": True})

    users = []
    
    async for user in cursor:
        users.append({
            "id": str(user["_id"]),
            "name": user.get("name"),
            "email": user.get("email")
        })

    return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Online users list",
                "data": users
            }
        )
