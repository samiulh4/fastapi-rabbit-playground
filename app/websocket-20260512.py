from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from bson import ObjectId
from app.database import user_collection, messages_collection, connections_collection
from app.models import Message, ConnectionStore
from user_agents import parse

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
            "status_code": 4004,
            "success": False,
            "message": "User not found",
            "data": []
        })
        await websocket.close(code=4004, reason="User not found")
        return
    
    websocket_object_id  = str(id(websocket))
    connection_id = str(uuid.uuid4())
    ua_raw = websocket.headers.get("user-agent", "")
    ua = parse(ua_raw)
    ua_string = (
        f"Browser: {ua.browser.family} {ua.browser.version_string} | "
        f"OS: {ua.os.family} {ua.os.version_string} | "
        f"Device: {ua.device.family} | "
        f"Mobile: {ua.is_mobile} | Tablet: {ua.is_tablet} | PC: {ua.is_pc} | Bot: {ua.is_bot}"
    )
    conn_store = ConnectionStore(
        user_id=str(user),
        connection_id=connection_id,
        websocket_object_id=websocket_object_id,
        status="connected",
        client_ip=websocket.client.host if websocket.client else "unknown",
        server_ip=websocket.base_url.hostname if websocket.base_url else "unknown",
        user_agent=ua_string if ua_raw else "unknown"
    )
    conn_dict = conn_store.model_dump()
    conn_dict["user_id"] = ObjectId(user)
    await connections_collection.insert_one(conn_dict)

    connections.append({
        "websocket": websocket,
        "user": user
    })

    try:
        while True:
            data = await websocket.receive_text()

            message = Message(sender_id=user, content=data)
            message_dict = message.model_dump()
            message_dict["sender_id"] = ObjectId(user)
            message_dict["connection_id"] = connection_id
            await messages_collection.insert_one(message_dict)

            dead = []
            for conn in connections:
                try:
                    await conn["websocket"].send_json({
                        "sender_id": user,
                        "content": data,
                    })
                except Exception:
                    dead.append(conn)
            for d in dead:
                connections.remove(d)

    except WebSocketDisconnect:
        connections[:] = [c for c in connections if c["websocket"] != websocket]
        await connections_collection.update_one(
            {"connection_id": connection_id},
            {"$set": {"status": "disconnected", "disconnected_at": datetime.now(timezone.utc)}}
        )
        print(f"{user} disconnected")

    except Exception as e:
        print(f"WebSocket error for {user}: {e}")
        connections[:] = [c for c in connections if c["websocket"] != websocket]
        await connections_collection.update_one(
            {"connection_id": connection_id},
            {"$set": {"status": "disconnected", "disconnected_at": datetime.now(timezone.utc)}}
        )
        try:
            await websocket.close(code=1011, reason="Internal server error")
            await websocket.send_json({
                "status_code": 1011,
                "success": False,
                "message": "Internal server error",
                "data": []
            })
        except Exception:
            await websocket.send_json({
                "status_code": 1011,
                "success": False,
                "message": str(e),
                "data": []
            })
