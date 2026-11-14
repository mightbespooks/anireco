from datetime import date
from pathlib import Path
from sqlalchemy import create_engine, JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

engine = create_engine("sqlite:///database.db", echo=False)
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(nullable=False)
    last_updated: Mapped[str | None]
    pfp: Mapped[str | None]

class Anime(Base):
    __tablename__ = "anime"

    anime_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    anilist_id: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[dict] = mapped_column(JSON, nullable=False)
    format: Mapped[str] = mapped_column()
    episodes: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column()
    start_date: Mapped[date] = mapped_column()
    end_date: Mapped[date] = mapped_column()
    mean_score: Mapped[int] = mapped_column()
    popularity: Mapped[int] = mapped_column()
    source: Mapped[str] = mapped_column()
    cover: Mapped[str] = mapped_column()

class User_Anime(Base):
    __tablename__ = "users_anime"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.anime_id"), primary_key=True)
    list_status: Mapped[str] = mapped_column()
    score: Mapped[float] = mapped_column()

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

class Director(Base):
    __tablename__ = "directors"

    director_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    anilist_id: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)

class AnimeDirector(Base):
    __tablename__ = "anime_directors"

    director_id: Mapped[int] = mapped_column(ForeignKey("directors.director_id"), primary_key=True)
    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.anime_id"), primary_key=True)

class UserDirectorAffinity(Base):
    __tablename__ = "user_director_affinities"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    director_id: Mapped[int] = mapped_column(ForeignKey("directors.director_id"), primary_key=True)
    mean: Mapped[float] = mapped_column()
    count: Mapped[int] = mapped_column()
    multiplier: Mapped[float] = mapped_column()

class AnilistRecommendations(Base):
    __tablename__ = "anilist_recommendations"

    anime_id: Mapped[int] = mapped_column(ForeignKey("anime.anime_id"), primary_key=True)
    recommended_anime_id: Mapped[int] = mapped_column(ForeignKey("anime.anime_id"), primary_key=True)
    rank: Mapped[int] = mapped_column()

Base.metadata.create_all(engine)
print(f"Database created successfully, located at: {Path(engine.url.database).resolve()}")