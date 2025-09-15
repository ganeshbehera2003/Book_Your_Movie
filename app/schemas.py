from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Movie
class MovieCreate(BaseModel):
    title: str
    price: float
    duration_min: int

class MovieOut(MovieCreate):
    id: int
    class Config: from_attributes = True

# Theater
class TheaterCreate(BaseModel):
    name: str
    city: str

class TheaterOut(TheaterCreate):
    id: int
    class Config: from_attributes = True

# Hall & Layout
class HallRowIn(BaseModel):
    label: str
    seat_count: int = Field(ge=6)

class HallCreate(BaseModel):
    theater_id: int
    name: str
    rows: List[HallRowIn]

class HallOut(BaseModel):
    id: int
    theater_id: int
    name: str
    class Config: from_attributes = True

class SeatOut(BaseModel):
    id: int
    hall_id: int
    row_label: str
    number: int
    is_aisle: bool
    class Config: from_attributes = True

# Show
class ShowCreate(BaseModel):
    hall_id: int
    movie_id: int
    start_time: datetime
    end_time: datetime

class ShowOut(ShowCreate):
    id: int
    class Config: from_attributes = True

# Booking
class BookingRequest(BaseModel):
    show_id: int
    seats: Optional[List[int]] = None  # explicit seat IDs
    group_size: Optional[int] = None   # find contiguous block of this size

class BookingOut(BaseModel):
    id: int
    show_id: int
    total_price: float
    status: str
    seat_ids: List[int]

class SuggestionOut(BaseModel):
    show_id: int
    hall_id: int
    start_time: datetime
    seat_ids: List[str]

# Analytics
class AnalyticsOut(BaseModel):
    movie_id: int
    start_time: datetime
    end_time: datetime
    tickets: int
    gmv: float
