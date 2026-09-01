# Voice Notes

A small end-to-end voice transcription app: an Expo (React Native) mobile app that
records speech, sends it to a FastAPI backend, which transcribes it with Deepgram
and stores the result.

```
iPhone / Simulator (Expo app)
  Record screen ── expo-audio records .m4a ──► POST /transcriptions (multipart)
                                                    │ FastAPI
                                                    ├─► Deepgram prerecorded API (nova-3)
                                                    ├─► SQLite (stand-in for Postgres)
                                                    ◄── { id, transcript, created_at }
  Transcript screen ◄── navigates with the result; also GET /transcriptions history
```

## Packages

- `api/` — Python FastAPI backend. Layered as `routers/` (validate + delegate) →
  `services/` (orchestration, deps injected) → `repos/` (SQLAlchemy data access),
  with the Deepgram HTTP call isolated in `clients/deepgram.py`.
- `app-mobile/` — Expo app (SDK 57, TypeScript, expo-router). Screens talk to
  hooks in `src/stores/`, which are the only consumers of the typed API client
  in `src/lib/api/`. `generated.ts` there is auto-generated from the backend's
  OpenAPI spec — CI fails if it drifts.

## Prerequisites

- **Python 3.12+** and **Node 20+**
- A **Deepgram API key** — free at [console.deepgram.com](https://console.deepgram.com)
  ($200 credit, no card required)
- For the iOS Simulator: Xcode. For a physical iPhone: the
  [Expo Go](https://expo.dev/go) app (phone and Mac must be on the same Wi-Fi).

## Run it locally

### 1. Backend

```sh
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # then edit .env and paste your DEEPGRAM_API_KEY

uvicorn main:app --host 0.0.0.0 --port 8000
```

`--host 0.0.0.0` matters: it lets your phone reach the backend over the LAN.
The SQLite database (`voice_notes.db`) is created automatically on first run.

Sanity check from another terminal:

```sh
curl -F "file=@some-audio.m4a" http://localhost:8000/transcriptions
```

### 2. Mobile app

In a second terminal:

```sh
cd app-mobile
npm install
npm start
```

Then either:

- press **`i`** to open the iOS Simulator (its mic uses your Mac's microphone), or
- scan the QR code with the **Expo Go** app on your iPhone.

No URL configuration is needed: the app derives the backend address from the
Expo dev server's host (`src/lib/api/request.ts`), which resolves correctly for
both the simulator and a phone on the same network. To point at a different
backend, set `EXPO_PUBLIC_API_URL`:

```sh
EXPO_PUBLIC_API_URL=http://192.168.1.50:8000 npm start
```

### 3. Use it

Tap the mic button, speak, tap again to stop — the recording uploads, Deepgram
transcribes it, and the app navigates to the Transcript screen showing the new
transcript with earlier ones listed below.

## Development

```sh
# backend lint + tests (fixture-driven, no DB or network needed)
cd api && .venv/bin/ruff check . && .venv/bin/pytest

# mobile typecheck
cd app-mobile && npx tsc --noEmit

# regenerate the typed API client after changing backend routes/models
cd app-mobile && npm run generate:api
```

CI (GitHub Actions) runs all of the above on every push, including a **codegen
drift check** that regenerates the client and fails if the committed
`src/lib/api/generated.ts` is stale.
