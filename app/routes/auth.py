from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.database import user_collection
from app.models import User, LoginRequest, LogoutRequest
from app.utils import get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post('/register')
async def auth_register(user: User):
    existing_user = await user_collection.find_one({"email": user.email})
    if existing_user:
        return JSONResponse(
            status_code=409,
            content={
                "success": False,
                "message": "User with this email already exists.",
                "data": []
            }
        )
    user_dict = user.model_dump()
    hashed_password = get_password_hash(user.password)
    user_dict["password"] = hashed_password
    result = await user_collection.insert_one(user_dict)
    return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "User created successfully.",
                "data": {
                    "user": {
                        "id": str(result.inserted_id),
                        "email": user_dict["email"]
                    }
                }
            }
        )

@router.post('/login')
async def auth_login(credentials: LoginRequest):
    user = await user_collection.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user.get("password", "")):
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "message": "Invalid email or password.",
                "data": []
            }
        )

    await user_collection.update_one(
        {"_id" : user["_id"]},
        {"$set":{
               "is_online":True 
            }
        }
    )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Logged in successfully.",
            "data": {
                "user": {
                    "id": str(user["_id"]),
                    "email": user["email"],
                    "name": user["name"]
                }
            }
        }
    )

@router.post('/logout')
async def auth_logout(request: LogoutRequest):
    request_dict = request.model_dump()
    await user_collection.update_one(
        {"email" : request_dict["email"]},
        {"$set":{
               "is_online":False 
            }
        }
    )

    return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Logout successfully.",
                "data": []
            }
        )
