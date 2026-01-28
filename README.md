# Pastebin-Lite (Python + Django)

A small Pastebin-like web application that allows users to create text pastes, generate shareable links, and view the content via those links. Pastes can optionally expire based on time (TTL) or number of views.

This project was built as a take-home assignment and focuses on backend correctness, API design, and robustness rather than UI styling.

---

## Features

- Create a text paste via API or UI
- Generate a unique, shareable URL for each paste
- View paste content in browser (HTML)
- Optional expiration:
  - Time-based expiration (TTL)
  - View-count based expiration
- Paste becomes unavailable (404) once expired
- Safe rendering (prevents script execution / XSS)
- Health check endpoint for service monitoring

---

## Tech Stack

- **Backend:** Python, Django, Django REST Framework
- **Database:** SQLite (local development)
- **Templates:** Django Templates (HTML)
- **Persistence:** Django ORM (can be easily switched to PostgreSQL for production)

---

## API Endpoints

### Health Check
GET /api/healthz


Response:
```json
{ "ok": true }
Create Paste
POST /api/pastes
Request Body (JSON):

{
  "content": "Hello world",
  "ttl_seconds": 60,
  "max_views": 5
}
Response:

{
  "id": "uuid",
  "url": "http://<host>/p/<uuid>"
}
Fetch Paste (API)
GET /api/pastes/<id>
Response:

{
  "content": "Hello world",
  "remaining_views": 4,
  "expires_at": "2026-01-01T00:00:00Z"
}
Each successful fetch counts as one view

Returns HTTP 404 if paste is expired, missing, or view limit exceeded

View Paste (HTML)
GET /p/<id>
Renders paste content in HTML

Content is safely escaped (no script execution)

Returns 404 page if paste is unavailable

Deterministic Time for Testing
If the environment variable below is set:

TEST_MODE=1
Then the request header:

x-test-now-ms: <milliseconds since epoch>
is used as the current time only for expiry logic.
If the header is absent, system time is used.

This is implemented to support deterministic automated testing.

How to Run Locally
1. Clone the repository
git clone <your-repo-url>
cd Pastebin_app
2. Create and activate virtual environment
python -m venv venv
Windows:

venv\Scripts\activate
Mac/Linux:

source venv/bin/activate
3. Install dependencies
pip install django djangorestframework
4. Run migrations
python manage.py makemigrations
python manage.py migrate
5. Start the server
python manage.py runserver
Open in browser:

Create Paste UI: http://127.0.0.1:8000/create

Health Check: http://127.0.0.1:8000/api/healthz

Persistence Layer
SQLite is used for local development via Django ORM.

The application does not rely on in-memory storage.

Can be deployed with PostgreSQL or any other supported database without code changes.

Design Decisions
UUIDs are used for paste IDs to prevent guessable URLs.

Expiry time is stored as an absolute timestamp (expires_at) for simpler and safer checks.

View count is incremented only on successful access to avoid negative values.

Django templates are used for UI to keep the project simple and robust.

API-first design with proper HTTP status codes.

Notes
UI styling is minimal as it is not heavily graded.

Focus is on correctness, robustness, and meeting all functional requirements.

