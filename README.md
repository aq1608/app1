# SUICINO

A Flask mental-health support web app: daily mood check-ins, a peer forum,
a gamified rewards system, and a therapist-matching questionnaire.

> **Note:** This project targets a sensitive domain (mental health / suicidal
> ideation). The crisis-support flow is currently a keyword-matching prototype
> and does **not** replace real crisis services. Before any real deployment,
> surface genuine hotline resources (e.g. 988 in the US) prominently.

## Structure

```
app.py                  # Main app (Flask + SQLAlchemy) — the canonical version
models.py               # SQLAlchemy models (User, Therapist, DailyCheckIn, ForumPost, ...)
forms.py                # WTForms (login, registration, questionnaire)
config.py               # Config loaded from environment (.env)
templates/              # Jinja2 templates
static/                 # css / js / uploads
legacy/                 # Archived code kept for reference (not run):
  app-json-prototype.py #   older JSON-file version — the only place the chatbot
                        #   / crisis-detection code currently lives
  data/                 #   JSON data used by that prototype
  templates/            #   old *-prev.html template backups
music-app/              # An unrelated music-player app that used to share this repo.
                        # Self-contained; consider moving to its own repository.
```

## Setup

```bash
python -m venv venv
# Windows: venv\Scripts\activate   |  macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file (not committed):

```
SECRET_KEY=change-me
DATABASE_URL=sqlite:///suicino.db
# Optional mail settings:
# MAIL_SERVER=...
# MAIL_USERNAME=...
# MAIL_PASSWORD=...
```

## Run

```bash
python app.py
```

The database tables are created automatically on first run.

## Known issues / TODO

- `models.py`: `User.total_points` is still a comment, not a column, so the
  `/rewards` route will raise `AttributeError`. Add the column.
- The SQLAlchemy app has no task-completion or forum-like routes yet (the JS in
  `static/js/main.js` calls endpoints that only existed in the JSON prototype).
- `/admin` (Flask-Admin) has **no authentication** — restrict it before deploying.
- Port the chatbot / crisis-detection from `legacy/app-json-prototype.py` if wanted.
- Turn off `debug=True` outside local development.

## Music app

`music-app/` is a separate Flask app for uploading and playing audio files.
Run it from inside its own folder:

```bash
cd music-app
python app.py
```
