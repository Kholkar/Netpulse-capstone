# CommerceHub Order API

A small FastAPI order-management API using a layered architecture and in-memory
storage. Orders are cleared when the server restarts.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for Swagger UI.

## Endpoints

- `GET /health` checks API availability.
- `POST /orders` validates and saves an order, returning its sequential ID and
  calculated total.
- `GET /orders` lists saved orders.

## Tests

```bash
python -m pytest -q
```

Swagger verification screenshots are in `evidence/`. The previous NetPulse
device-monitoring project is preserved in `netpulse-capstone/`.# netpulse-capstone

NetPulse is a small FastAPI device-monitoring API. It stores devices and alerts
in memory and records one alert when a device changes from online to offline.
It does not ping devices or use a database; data resets when the app restarts.

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