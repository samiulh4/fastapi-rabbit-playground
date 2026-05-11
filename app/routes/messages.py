from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.database import messages_collection
from app.models import Message
from bson import ObjectId

router = APIRouter(prefix="/message", tags=["messages"])

@router.post('/send')
async def message_send(message: Message):
    message_dump = message.model_dump()
    message_dump["sender_id"] = ObjectId(message_dump["sender_id"]) 
    result = await messages_collection.insert_one(message_dump)
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

@router.get('/list')
async def message_list():
    cursor = messages_collection.aggregate([
        {"$match": {"is_active": True}},
        {"$lookup": {
            "from": "users",
            "localField": "sender_id",
            "foreignField": "_id",
            "as": "sender"
        }},
        {"$unwind": "$sender"},
        {"$sort": {"_id": 1}}
    ])

    messages = []
    
    async for message in cursor:
        messages.append({
            "id": str(message["_id"]),
            "sender_id": str(message["sender_id"]),
            "sender_name": message["sender"].get("name"),
            "sender_email": message["sender"].get("email"),
            "content": message.get("content"),
            "created_at": message.get("created_at").isoformat()
        })

    return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Active messages list",
                "data": messages
            }
        )
