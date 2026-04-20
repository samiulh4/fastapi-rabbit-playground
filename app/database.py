from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_URL)

db = client["mongo_rabbit_playground"]

users_collection = db["users"]
#messages_collection = db["messages"]
#notifications_collection = db["notifications"]
#events_collection = db["events"]