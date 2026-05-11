from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_URL)

db = client["mongo_rabbit_playground"]

user_collection = db["users"]
messages_collection = db["messages"]
connections_collection = db["connections"]
#notifications_collection = db["notifications"]
#events_collection = db["events"]