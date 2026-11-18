import requests
import queries as gql
import functions.helpers as helpers
import functions.calculations as calculations
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import *

ANILIST_URL = "https://graphql.anilist.co"
STAFF_ROLES = {
    "director", "chief director", "assistant director", "art director", 
    "series composition", "script", "original story", "original character design", "music"
}

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_or_create_entity(db, model, cache_map, lookup_key, create_attrs, id_field_name):
    if lookup_key not in cache_map:
        entity = model(**create_attrs)
        db.add(entity)
        db.flush()
        cache_map[lookup_key] = getattr(entity, id_field_name)
    return cache_map[lookup_key]

@app.post("/api/import_user")
async def import_user(username: str, db: Session = Depends(get_db)):
    response = requests.post(ANILIST_URL, json={
        "query": gql.IMPORT_USER,
        "variables": {"username": username}
    })
    data = response.json().get("data")

    genre_map = {genre.name: genre.genre_id for genre in db.query(Genre).all()}
    tag_map = {tag.name: tag.tag_id for tag in db.query(Tag).all()}
    studio_map = {studio.anilist_id: studio.studio_id for studio in db.query(Studio).all()}
    staff_map = {staff.anilist_id: staff.staff_id for staff in db.query(Staff).all()}
    lists = data.get("MediaListCollection").get("lists")
    existing_map = {
        anime.anilist_id: anime 
        for anime in db.query(Anime).all()
    }

    user = data.get("User")
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        existing_user.last_updated = datetime.now() 
        existing_user.pfp = user.get("avatar").get("large")
        current_user_id = existing_user.user_id
    else:
        new_user = User(
            username = username,
            last_updated = datetime.now(),
            pfp = user.get("avatar").get("large")
        )
        db.add(new_user)
        db.flush()
        current_user_id = new_user.user_id

    raw_anime = []
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
                db.flush()
                existing_map[anilist_id] = new_anime
                existing_anime = new_anime

            list_status = entry.get("status")
            user_score = entry.get("score") or 0

            db.merge(User_Anime(
                user_id = current_user_id,
                anime_id = existing_map[anilist_id].anime_id,
                list_status = list_status,
                score = user_score
            ))

            for genre in media.get("genres", []):
                genre_id = get_or_create_entity(
                    db = db,
                    model = Genre,
                    cache_map = genre_map,
                    lookup_key = genre,
                    create_attrs = {"name": genre},
                    id_field_name = "genre_id"
                )

                db.merge(AnimeGenre(
                    anime_id = existing_anime.anime_id,
                    genre_id = genre_id
                ))

            for tag in media.get("tags", []):
                tag_name = tag.get("name")
    
                tag_id = get_or_create_entity(
                    db = db,
                    model = Tag,
                    cache_map = tag_map,
                    lookup_key = tag_name,
                    create_attrs = {"name": tag_name},
                    id_field_name = "tag_id"
                )

                db.merge(AnimeTag(
                    anime_id = existing_anime.anime_id,
                    tag_id = tag_id,
                    similarity = tag.get("rank", 0)
                ))

            for studio_edge in media.get("studios", {}).get("edges", []):
                studio_node = studio_edge.get("node", {})
                studio_anilist_id = studio_node.get("id")
                studio_name = studio_node.get("name")

                if not studio_edge.get("isMain"):
                    continue 

                studio_id = get_or_create_entity(
                    db = db,
                    model = Studio,
                    cache_map = studio_map,
                    lookup_key = studio_anilist_id,
                    create_attrs = {"anilist_id": studio_anilist_id, "name": studio_name},
                    id_field_name = "studio_id"
                )

                db.merge(AnimeStudio(
                    anime_id = existing_anime.anime_id,
                    studio_id = studio_id
                ))

            for staff_edge in media.get("staff", {}).get("edges", []):
                role = staff_edge.get("role")
                if role.lower() not in STAFF_ROLES:
                    continue

                staff_node = staff_edge.get("node", {})
                staff_anilist_id = staff_node.get("id")
                staff_name = staff_node.get("name", {})
                full_name = " ".join(
                    p for p in [
                        staff_name.get("first"),
                        staff_name.get("last")
                    ]
                    if p
                )

                staff_id = get_or_create_entity(
                    db = db,
                    model = Staff,
                    cache_map = staff_map,
                    lookup_key = staff_anilist_id,
                    create_attrs = {"anilist_id": staff_anilist_id, "name": full_name},
                    id_field_name = "staff_id"
                )

                db.merge(AnimeStaff(
                    anime_id = existing_anime.anime_id,
                    staff_id = staff_id,
                    role = role
                ))

            for rank, rec_node in enumerate(media.get("recommendations", {}).get("nodes", []), start = 1):
                media_rec = rec_node.get("mediaRecommendation")
                if not media_rec:
                    continue

                rec_anilist_id = media_rec.get("id")
                
                db.merge(AnilistRecommendations(
                    anime_id = existing_anime.anime_id,
                    recommended_anime_id = rec_anilist_id,
                    rank = rank
                ))

            raw_anime.append({
                **media,  
                "list_status": list_status, 
                "score": user_score    
            })
    
    db.commit()

    return {
        "message": f"User {username} has been imported successfully!",
        "raw_anime": raw_anime
    }