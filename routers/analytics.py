from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func
from datetime import datetime
from deps import get_session
from models import Booking, Show
from schemas import AnalyticsOut

router = APIRouter()

@router.get("/movie", response_model=AnalyticsOut)
def movie_analytics(movie_id:int, start:datetime, end:datetime):
    with get_session() as db:
        if end <= start:
            raise HTTPException(400, "end must be after start")
        # join bookings->shows to filter by movie & time
        q = (
            select(func.count(), func.coalesce(func.sum(Booking.total_price), 0.0))
            .select_from(Booking)
            .join(Show, Show.id == Booking.show_id)
            .where(Show.movie_id == movie_id, Show.start_time >= start, Show.start_time <= end)
        )
        tickets, gmv = db.execute(q).one()
        return AnalyticsOut(movie_id=movie_id, start_time=start, end_time=end, tickets=int(tickets or 0), gmv=float(gmv or 0.0))
