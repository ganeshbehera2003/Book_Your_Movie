# Movie Booking API (FastAPI)

A production-ready, demoable REST API for movie ticket booking with:
- CRUD for movies, theaters, halls, shows, seats & prices
- Hall layout with variable-length rows (>= 6 seats) split into 3 blocks (creating exactly 6 aisle seats per row)
- Group booking with contiguous seats and concurrency-safe reservations
- Alternatives suggestion when contiguous seats aren't available
- Analytics (tickets + GMV) for a movie over a period

## Quick Start (Local)

```bash
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env  # edit if needed
uvicorn app.main:app --reload
```
Open docs: http://localhost:8000/docs

### Env
- `DATABASE_URL` (default sqlite: // /./booking.db)

## Deploy (Free-ish options)
- **Railway** or **Render** (recommended for free tiers)
- **Fly.io** (global free hobby tier)
- **Heroku** (if you have a free/eco dyno)

### Heroku (example)
```bash
heroku create movie-booking-api-demo
heroku buildpacks:add heroku/python
heroku config:set DATABASE_URL=postgresql+psycopg2://...  # from Heroku Postgres addon
git push heroku main
```

## Domain Model
- Movie(id, title, price, duration_min)
- Theater(id, name, city)
- Hall(id, theater_id, name)
- HallRow(id, hall_id, label, seat_count)
- Seat(id, hall_id, row_label, number, is_aisle)
- Show(id, hall_id, movie_id, start_time, end_time)
- Booking(id, show_id, total_price, status)
- BookingSeat(booking_id, show_id, seat_id)  // (show_id, seat_id) UNIQUE to prevent double-booking

## Concurrency
We rely on DB-level uniqueness of `(show_id, seat_id)` in `booking_seats`. Bookings are made in a transaction; conflicting inserts raise `IntegrityError` and are handled gracefully.
