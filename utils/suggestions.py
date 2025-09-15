from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timedelta
from models import Show, Seat, BookingSeat
from .seating import find_contiguous_block

# Suggest up to N alternative shows of the same movie in same theater (or city), with contiguous seats

def suggest_alternatives(session: Session, movie_id: int, hall_id: int, group_size: int, when: datetime, limit: int = 5):
    # Look +/- 1 day around the given time within same hall first, then any hall in same theater
    q = select(Show).where(
        Show.movie_id == movie_id,
        Show.start_time >= when - timedelta(days=1),
        Show.start_time <= when + timedelta(days=1)
    ).order_by(Show.start_time)
    shows = session.scalars(q).all()

    suggestions = []
    for show in shows:
        # Get available seats for this show
        booked = set([sid for (sid,) in session.query(BookingSeat.seat_id).filter(BookingSeat.show_id == show.id).all()])
        seats = session.query(Seat).filter(Seat.hall_id == show.hall_id).all()
        by_row = {}
        for s in seats:
            if s.id in booked: continue
            by_row.setdefault(s.row_label, []).append(s)
        found: Optional[List[int]] = None
        for row_label, row_seats in by_row.items():
            row_seats.sort(key=lambda x: x.number)
            avail_nums = [r.number for r in row_seats]
            block = find_contiguous_block(avail_nums, group_size)
            if block:
                # map numbers to seat ids
                num_to_seat_label = {r.number: f"{r.row_label}{r.number}" for r in row_seats}
                found = [num_to_seat_label[n] for n in block]
                break
        if found:
            suggestions.append({
                "show_id": show.id,
                "hall_id": show.hall_id,
                "start_time": show.start_time,
                "seat_ids": found,
            })
            if len(suggestions) >= limit:
                break
    return suggestions
