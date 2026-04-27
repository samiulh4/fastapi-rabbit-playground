from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from app.models import Message, User
from app.database import user_collection
from app.database import messages_collection
from pwdlib import PasswordHash

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

@app.post('/user/create')
async def create_user(user: User):
    existing_user = await user_collection.find_one({"email": user.email})
    if existing_user:
        return {"message": "User with this email already exists"}
    #user.password = user.password[:72]  # Truncate password to 72 bytes to comply with bcrypt limit
    user_dict = user.model_dump()
    hashed_password = get_password_hash(user.password)
    user_dict["password"] = hashed_password
    result = await user_collection.insert_one(user_dict)
    return {
        "message": "User created successfully",
        "email": user_dict["email"],
        "id": str(result.inserted_id)
    }

@app.post('/message/create')
async def create_message(message: Message):
    message_dict = message.model_dump()
    result = await messages_collection.insert_one(message_dict)
    return {
        "message": "Message created successfully",
        "id": str(result.inserted_id)
    }

def get_password_hash(password : str) -> str:
    password_hash = PasswordHash.recommended()
    return password_hash.hash(password)