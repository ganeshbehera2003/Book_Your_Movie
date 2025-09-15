from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from schemas import MovieCreate, MovieOut
from models import Movie
from deps import get_session

router = APIRouter()

@router.post("/", response_model=MovieOut)
def create_movie(payload: MovieCreate):
    with get_session() as db:
        exists = db.scalar(select(Movie).where(Movie.title==payload.title))
        print(exists,"+==========================================================")
        if exists:
            raise HTTPException(400, "Movie with this title already exists")
        m = Movie(**payload.model_dump())
        db.add(m)
        db.commit()
        return m

@router.get("/", response_model=list[MovieOut])
def list_movies():
    with get_session() as db:
        return db.scalars(select(Movie)).all()

@router.get("/{movie_id}", response_model=MovieOut)
def get_movie(movie_id: int):
    with get_session() as db:
        m = db.get(Movie, movie_id)
        if not m: raise HTTPException(404, "Not found")
        return m

@router.put("/{movie_id}", response_model=MovieOut)
def update_movie(movie_id: int, payload: MovieCreate):
    with get_session() as db:
        m = db.get(Movie, movie_id)
        if not m: raise HTTPException(404, "Not found")
        for k,v in payload.model_dump().items(): setattr(m,k,v)
        db.flush(); return m

@router.delete("/{movie_id}")
def delete_movie(movie_id: int):
    with get_session() as db:
        m = db.get(Movie, movie_id)
        if not m: raise HTTPException(404, "Not found")
        db.delete(m)
        return {"ok": True}
