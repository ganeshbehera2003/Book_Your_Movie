from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from schemas import TheaterCreate, TheaterOut
from models import Theater
from deps import get_session

router = APIRouter()


@router.post("/", response_model=TheaterOut)
def create_theater(payload: TheaterCreate):
    with get_session() as db:
        t = Theater(**payload.model_dump())
        db.add(t)
        db.flush()
        return t


@router.get("/", response_model=list[TheaterOut])
def list_theaters():
    with get_session() as db:
        return db.scalars(select(Theater)).all()


@router.get("/{theater_id}", response_model=TheaterOut)
def get_theater(theater_id: int):
    with get_session() as db:
        t = db.get(Theater, theater_id)
        if not t:
            raise HTTPException(404, "Not found")
        return t


@router.delete("/{theater_id}")
def delete_theater(theater_id: int):
    with get_session() as db:
        t = db.get(Theater, theater_id)
        if not t:
            raise HTTPException(404, "Not found")
        db.delete(t)
        return {"ok": True}
