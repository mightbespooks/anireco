import sys
from datetime import date
from pathlib import Path
from sqlalchemy import create_engine, JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'database.db'}"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

INITIAL_GENRES = [
    "Action", "Adventure", "Comedy", "Drama", "Ecchi", "Fantasy", 
    "Horror", "Mahou Shoujo", "Mecha", "Music", "Mystery", "Psychological", 
    "Romance", "Sci-Fi", "Slice of Life", "Sports", "Supernatural", "Thriller"
]

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column()
    last_updated: Mapped[str] = mapped_column()
    pfp: Mapped[str] = mapped_column()

class Anime(Base):
    __tablename__ = "anime"

    anime_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    anilist_id: Mapped[int] = mapped_column(unique=True)
    title: Mapped[dict] = mapped_column(JSON)
    format: Mapped[str] = mapped_column(nullable=True)
    episodes: Mapped[int] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=True)
    start_date: Mapped[date | None] = mapped_column(nullable=True) 
    end_date: Mapped[date | None] = mapped_column(nullable=True)
    mean_score: Mapped[int] = mapped_column(nullable=True)
    popularity: Mapped[int] = mapped_column(nullable=True)
    source: Mapped[str] = mapped_column(nullable=True)
    cover: Mapped[str] = mapped_column(nullable=True)

class User_Anime(Base):
    __tablename__ = "users_anime"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.anime_id"), primary_key=True)
    list_status: Mapped[str] = mapped_column()
    score: Mapped[float | None] = mapped_column(nullable=True)

class Genre(Base):
    __tablename__ = "genres"

    genre_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)

class AnimeGenre(Base):
    __tablename__ = "anime_genres"

    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.genre_id"), primary_key=True)
    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.anime_id"), primary_key=True)

class UserGenreAffinity(Base):
    __tablename__ = "user_genre_affinities"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.genre_id"), primary_key=True)
    mean: Mapped[float] = mapped_column()
    count: Mapped[int] = mapped_column()
    multiplier: Mapped[float] = mapped_column()

class Tag(Base):
    __tablename__ = "tags"

    tag_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)

class AnimeTag(Base):
    __tablename__ = "anime_tags"

    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.tag_id"), primary_key=True)
    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.anime_id"), primary_key=True)
    similarity: Mapped[int] = mapped_column()

class UserTagAffinity(Base):
    __tablename__ = "user_tag_affinities"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.tag_id"), primary_key=True)
    mean: Mapped[float] = mapped_column()
    count: Mapped[int] = mapped_column()
    multiplier: Mapped[float] = mapped_column()

class Studio(Base):
    __tablename__ = "studios"

    studio_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    anilist_id: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)

class AnimeStudio(Base):
    __tablename__ = "anime_studios"

    studio_id: Mapped[int] = mapped_column(ForeignKey("studios.studio_id"), primary_key=True)
    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.anime_id"), primary_key=True)

class UserStudioAffinity(Base):
    __tablename__ = "user_studio_affinities"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    studio_id: Mapped[int] = mapped_column(ForeignKey("studios.studio_id"), primary_key=True)
    mean: Mapped[float] = mapped_column()
    count: Mapped[int] = mapped_column()
    multiplier: Mapped[float] = mapped_column()

class Staff(Base):
    __tablename__ = "staff"

    staff_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    anilist_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)

class AnimeStaff(Base):
    __tablename__ = "anime_staff"

    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.anime_id"), primary_key=True)
    staff_id: Mapped[int] = mapped_column(ForeignKey("staff.staff_id"), primary_key=True)
    role: Mapped[str] = mapped_column(primary_key=True)

class UserStaffAffinity(Base):
    __tablename__ = "user_staff_affinities"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    staff_id: Mapped[int] = mapped_column(ForeignKey("staff.staff_id"), primary_key=True)
    mean: Mapped[float] = mapped_column()
    count: Mapped[int] = mapped_column()
    multiplier: Mapped[float] = mapped_column()

class AnilistRecommendations(Base):
    __tablename__ = "anilist_recommendations"

    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.anime_id"), primary_key=True)
    recommended_anime_id: Mapped[int] = mapped_column(ForeignKey("anime.anime_id"), primary_key=True)
    rank: Mapped[int] = mapped_column()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    db_path = Path(engine.url.database).resolve()
    Base.metadata.create_all(engine)

    db = SessionLocal()
    try:
        for genre in INITIAL_GENRES:
            db.add(Genre(name=genre))
        db.commit()
    finally:
        db.close()

    print(f"Database created successfully, located at: {db_path}")