# app/main.py
from fastapi import FastAPI
from db import engine, Base
from routers import movies, theaters, halls, shows, bookings, analytics

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Movie Ticket Booking API")

# Routers
app.include_router(movies.router, prefix="/movies", tags=["Movies"])
app.include_router(theaters.router, prefix="/theaters", tags=["Theaters"])
app.include_router(halls.router, prefix="/halls", tags=["Halls"])
app.include_router(shows.router, prefix="/shows", tags=["Shows"])
app.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

@app.get("/")
def root():
    return {"message": "Movie Ticket Booking API is running"}