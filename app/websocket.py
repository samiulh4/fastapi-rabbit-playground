from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from bson import ObjectId
from app.database import user_collection, messages_collection, connections_collection

# Global connections list
connections = []

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/message/{user}")
async def websocket_endpoint(websocket: WebSocket, user: str):
    await websocket.accept()
    
    try:
        existing_user = await user_collection.find_one({"_id": ObjectId(user)})
    except:
        existing_user = None
    
    if not existing_user:
        await websocket.send_json({
            "success": False,
            "message": "User not found",
            "data": []
        })
        await websocket.close(code=4004, reason="User not found")
        return
    
    session_id = str(id(websocket))
    connection = {}
    connection['user_id'] = ObjectId(user)
    connection['session_id'] = session_id
    connection['ip_address'] = websocket.client.host if websocket.client else "unknown"
    connection['status'] = "connected"
    connection['connected_at'] = datetime.now(timezone.utc)
    await connections_collection.insert_one(connection)

    connections.append({
        "websocket": websocket,
        "user": user
    })

    try:
        while True:
            data = await websocket.receive_text()

            for connection in connections:
                await connection["websocket"].send_json({
                    "sender_id": user,
                    "content": data,
                })

    except WebSocketDisconnect:
        # remove disconnected user
        connections[:] = [c for c in connections if c["websocket"] != websocket]
        await connections_collection.update_one({
            "session_id": session_id
        },{
            "$set":{"status": "disconnected", "disconnected_at": datetime.now(timezone.utc)}
        })
        print(f"{user} disconnected")
