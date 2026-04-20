from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Fast API Rabbit Playground is Running"}

@app.post('/user/create')
async def create_user(user: dict):
    return {"message": "User created successfully"}