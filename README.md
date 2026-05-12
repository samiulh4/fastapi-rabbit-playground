# fastapi-rabbit-playground

A playground for learning **FastAPI**, **RabbitMQ**, **MongoDB**, and **WebSockets**. The app supports user registration/login, real-time messaging via WebSockets, and message brokering through RabbitMQ.

---

## Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| API         | FastAPI 0.136+                      |
| Database    | MongoDB (via Motor — async driver)  |
| Broker      | RabbitMQ (via aio-pika)             |
| Real-time   | WebSockets (built-in FastAPI)       |
| Auth        | bcrypt password hashing (passlib)   |

---

## Project Structure

```
app/
├── main.py            # App entry point, middleware, router registration
├── database.py        # MongoDB connection and collections
├── models.py          # Pydantic models (User, Message, ConnectionStore, etc.)
├── rabbitmq.py        # RabbitMQ publish and consume logic
├── websocket.py       # WebSocket connection manager and endpoint
├── utils.py           # Password hashing helpers
└── routes/
    ├── auth.py        # POST /auth/register, /auth/login, /auth/logout
    ├── users.py       # User management routes
    └── messages.py    # POST /message/send, GET /message/list
```

---

## Setup

### 1. Create and activate virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start RabbitMQ (Docker)

```bash
docker run -d \
  --hostname rabbit-host \
  --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3-management
```

| Flag                    | Meaning                          |
|-------------------------|----------------------------------|
| `-d`                    | Run in background                |
| `--hostname rabbit-host`| Container hostname               |
| `--name rabbitmq`       | Container name                   |
| `-p 5672:5672`          | AMQP port (app connection)       |
| `-p 15672:15672`        | Management web UI port           |
| `rabbitmq:3-management` | RabbitMQ image with dashboard    |

RabbitMQ dashboard: [http://localhost:15672](http://localhost:15672)  
Default credentials: `guest` / `guest`

### 4. Start MongoDB

Make sure MongoDB is running locally on the default port:

```bash
mongod --port 27017
```

Database used: `mongo_rabbit_playground`  
Collections: `users`, `messages`, `connections`

### 5. Run the API server

```bash
uvicorn app.main:app --reload
```

API docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## API Endpoints

### Auth — `/auth`

| Method | Endpoint          | Description              |
|--------|-------------------|--------------------------|
| POST   | `/auth/register`  | Register a new user      |
| POST   | `/auth/login`     | Login and set online     |
| POST   | `/auth/logout`    | Logout and set offline   |

### Messages — `/message`

| Method | Endpoint          | Description                              |
|--------|-------------------|------------------------------------------|
| POST   | `/message/send`   | Store a message in MongoDB               |
| GET    | `/message/list`   | List active messages with sender details |

### WebSocket

| Endpoint                  | Description                                   |
|---------------------------|-----------------------------------------------|
| `ws://localhost:8000/ws/message/{user_id}` | Real-time messaging channel |

---

## Message Flow

```
Client (WebSocket)
     │
     ▼
websocket.py  ──publish──►  RabbitMQ Queue (rabbitmq_playground_queue)
                                    │
                               consume() loop
                                    │
                                    ▼
                        manager.broadcast()  ──►  All connected WebSocket clients
```

1. A client sends a message over WebSocket.
2. The message is saved to MongoDB and published to RabbitMQ via `publish_message()`.
3. The `consume()` task (started at app startup) reads from the queue and broadcasts to all live WebSocket connections.

---

## RabbitMQ Concepts

### Exchange vs Queue

**Exchange** (message router):
- Receives messages from producers and routes them to queues.
- Does **not** store messages.
- Routing depends on routing key, bindings, and exchange type.

| Exchange Type | Routing Behaviour                   |
|---------------|-------------------------------------|
| `direct`      | Exact routing key match             |
| `fanout`      | Broadcast to all bound queues       |
| `topic`       | Pattern matching (`user.*`, `order.#`) |
| `headers`     | Based on message headers            |

**Queue** (message storage):
- Stores messages until consumed (FIFO).
- Messages remain until consumed, TTL expires, or manually deleted.

**Flow:**
```
Producer → Exchange → Queue → Consumer
```

---

## Dependency Management

```bash
# Freeze current environment
pip freeze > requirements.txt

# Install from file
pip install -r requirements.txt
```

