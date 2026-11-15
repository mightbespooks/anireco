import requests
import queries as gql
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db, User, Anime

ANILIST_URL = "https://graphql.anilist.co"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/import_user")
async def import_user(username: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="User already exists.")

    response = requests.post(ANILIST_URL, json={
        "query": gql.IMPORT_USER,
        "variables": {"username": username}
    })
    data = response.json().get("data")

    user = data.get("User")
    db.add(User(
        username = username,
        last_updated = datetime.now(),
        pfp = user.get("avatar").get("large")
    ))
    db.commit()
    
    return data
