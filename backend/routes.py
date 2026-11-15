import requests
import queries as gql
import functions.helpers as helpers
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
    response = requests.post(ANILIST_URL, json={
        "query": gql.IMPORT_USER,
        "variables": {"username": username}
    })
    data = response.json().get("data")

    user = data.get("User")
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        existing_user.last_updated = datetime.now() 
        existing_user.pfp = user.get("avatar").get("large")
    else:
        db.add(User(
            username = username,
            last_updated = datetime.now(),
            pfp = user.get("avatar").get("large")
        ))

    lists = data.get("MediaListCollection").get("lists")
    existing_map = {
        anime.anilist_id: anime 
        for anime in db.query(Anime).all()
    }
    
    for l in lists:
        if l.get("isCustomList"):
            continue

        for entry in l.get("entries", []):
            media = entry.get("media", {})
            if media.get("status") == "NOT_YET_RELEASED":
                continue

            anilist_id = media.get("id")
            fields = {
                "anilist_id": anilist_id,
                "title": media.get("title"),
                "format": media.get("format"),
                "episodes": media.get("episodes"),
                "status": media.get("status"),
                "start_date": helpers.format_date(media.get("startDate")),
                "end_date": helpers.format_date(media.get("endDate")),
                "mean_score": media.get("meanScore"),
                "popularity": media.get("popularity"),
                "source": media.get("source"),
                "cover": media.get("coverImage", {}).get("large"),
            }

            if anilist_id in existing_map:
                existing_anime = existing_map[anilist_id]
                for key, value in fields.items():
                    setattr(existing_anime, key, value)
            else:
                new_anime = Anime(**fields)
                db.add(new_anime)
                existing_map[anilist_id] = new_anime

    db.commit()

    return f"User {username} has been imported successfully!"