from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from app.models import Message, User, LoginRequest, LogoutRequest
from app.database import user_collection
from app.database import messages_collection
from pwdlib import PasswordHash
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Fast API Rabbit Playground is Running"}

@app.post('/auth/register')
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

@app.post('/auth/login')
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

@app.post('/auth/logout')
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

@app.get('/users/online')
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


@app.post('/message/create')
async def create_message(message: Message):
    message_dict = message.model_dump()
    result = await messages_collection.insert_one(message_dict)
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Message created successfully.",
            "data": {
                "id": str(result.inserted_id)
            }
        }
    )

def get_password_hash(password : str) -> str:
    password_hash = PasswordHash.recommended()
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    password_hash = PasswordHash.recommended()
    return password_hash.verify(password, hashed_password)