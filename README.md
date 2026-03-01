# webhook-repo

A Flask + MongoDB webhook receiver that captures GitHub events (Push, Pull Request, Merge) from [action-repo](https://github.com/devarshidubey/action-repo), stores them in MongoDB Atlas, and exposes an API for the UI to poll.

**Live URL:** [`https://webhook-repo-nfnj.onrender.com`](https://webhook-repo-nfnj.onrender.com)

---

## Architecture

```
action-repo (GitHub)
      │
      │  POST /webhook/receiver
      ▼
Flask API (Render)
      │
      │  insert_one()
      ▼
MongoDB Atlas
      │
      │  GET /events?after=<timestamp>
      ▼
React UI (polls every 15s)
```

---

## Tech Stack

- **Backend**: Flask, Gunicorn
- **Database**: MongoDB Atlas (via flask-pymongo)
- **Deployment**: Docker on Render
- **Structure**: Based on [flask-realworld-example-app](https://github.com/gothinkster/flask-realworld-example-app)

---

## Project Structure

```
webhook-repo/
├── conduit/
│   ├── webhook/
│   │   ├── __init__.py
│   │   ├── views.py        # Routes: POST /webhook/receiver, GET /events
│   │   ├── services.py     # Business logic, MongoDB operations
│   │   └── serializers.py  # Marshmallow schema validation
│   ├── app.py              # App factory (create_app)
│   ├── settings.py         # DevConfig, ProdConfig, TestConfig
│   ├── extensions.py       # PyMongo, CORS init
│   ├── exceptions.py       # InvalidUsage, error handlers
│   ├── commands.py         # Flask CLI commands
│   └── utils.py            # normalize_timestamp
├── requirements/
│   ├── prod.txt
│   └── dev.txt
├── requirements.txt        # Points to prod.txt
├── wsgi.py                 # Gunicorn entry point
└── Dockerfile
```

---

## API Endpoints

### `POST /webhook/receiver`
Receives GitHub webhook payloads and stores them to MongoDB.

**Headers required:**
```
X-Github-Event: push | pull_request
Content-Type: application/json
```

**Supported events:**

| GitHub Event   | Stored Action |
|----------------|---------------|
| `push`         | `PUSH`        |
| `pull_request` (opened) | `PULL_REQUEST` |
| `pull_request` (closed + merged) | `MERGE` |

**Response:**
```json
{ "message": "success" }
```

---

### `GET /events`
Returns stored events, sorted by timestamp descending.

**Query params:**

| Param   | Type   | Description                              |
|---------|--------|------------------------------------------|
| `after` | string | ISO 8601 UTC timestamp. Returns only events newer than this value. Used for cursor-based polling. |

**Example:**
```
GET /events?after=2026-03-01T06:39:19.667Z
```

**Response:**
```json
{
  "events": [
    {
      "request_id": "abc123",
      "author": "devarshidubey",
      "action": "PUSH",
      "from_branch": null,
      "to_branch": "main",
      "timestamp": "2026-03-01T06:37:06.000Z"
    }
  ]
}
```

---

## MongoDB Schema

| Field        | Type             | Description                                      |
|--------------|------------------|--------------------------------------------------|
| `_id`        | ObjectId         | MongoDB auto-generated ID (excluded from API)    |
| `request_id` | string           | Git commit hash (push) or PR ID (pull request)   |
| `author`     | string           | GitHub username                                  |
| `action`     | string           | `PUSH`, `PULL_REQUEST`, or `MERGE`               |
| `from_branch`| string or null   | Source branch (null for push events)             |
| `to_branch`  | string           | Target branch                                    |
| `timestamp`  | string (ISO UTC) | Time of the event, normalized to UTC             |

---

## Local Development

### Prerequisites
- Docker + Docker Compose
- MongoDB Atlas account (or local MongoDB)

### Setup

```bash
git clone https://github.com/devarshidubey/webhook-repo.git
cd webhook-repo
cp .env.example .env
# edit .env with your values
docker compose up --build
```

### Environment Variables

```env
MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/webhookdb
SECRET_KEY=your-secret-key
FLASK_ENV=development
FLASK_APP=wsgi.py
FLASK_DEBUG=1
```

### Running Tests

```bash
pip install -r requirements/dev.txt
flask test
```

### Linting

```bash
flask lint
flask lint --fix-imports   # auto-fix import order
```

---

## Deployment

Deployed on **Render** using Docker.

1. Push to `main` branch
2. Render automatically builds the Docker image and redeploys
3. Environment variables are configured in the Render dashboard
Alternatively you can use your own Docker Image to deploy, this is a safer approach because if the image works on your PC it will work in production.
---

## Setting Up the GitHub Webhook

1. Go to `action-repo` → **Settings** → **Webhooks** → **Add webhook**
2. Set **Payload URL** to `https://webhook-repo-nfnj.onrender.com/webhook/receiver`
3. Set **Content type** to `application/json`
4. Select **Let me select individual events** → check **Pushes** and **Pull requests**
5. Click **Add webhook**
