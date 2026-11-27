# netpulse-capstone

NetPulse is a small FastAPI device-monitoring API. It records one alert when a
device changes from online to offline. The default in-memory backend resets when
the app restarts; an optional MySQL backend persists devices and alerts.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for the Swagger UI.

## Try the alert flow

1. Register a device with `POST /devices`:

   ```json
   {
     "device_id": "RTR-101",
     "name": "Branch Router",
     "device_type": "router",
     "ip_address": "192.168.10.1",
     "status": "online"
   }
   ```

2. Send `{"status":"offline"}` to `PATCH /devices/RTR-101/status` twice.
3. Check `GET /alerts`; there should be one alert for `RTR-101`.

## Architecture

- Routes expose HTTP endpoints and translate service errors to HTTP responses.
- The service enforces device rules and detects online-to-offline transitions.
- The repository owns in-memory device and alert storage.
- The event function creates and stores the UTC offline alert.

## Tests

```bash
python -m pytest -q
```

## MySQL Persistence

Create the MySQL database and user, then copy `.env.example` to `.env`. Set
`PERSISTENCE_BACKEND=mysql` and update the connection values in `.env`. Do not
commit `.env`; it contains local credentials.

Install the declared dependencies and apply the schema:

```bash
python -m pip install -r requirements.txt
alembic upgrade head
alembic current
```

To evolve the schema, update the ORM model and generate a migration:

```bash
alembic revision --autogenerate -m "describe schema change"
alembic upgrade head
```

The in-memory backend remains the default for isolated service tests. The
SQLAlchemy repository uses the same repository contract.