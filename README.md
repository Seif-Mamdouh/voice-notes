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
  `services/` (orchestration, deps injected) → `repos/` (SQLAlchemy data access).
- `app-mobile/` — Expo app (TypeScript, expo-router). Screens talk to hooks in
  `stores/`, which are the only consumers of the typed API client in `lib/api/`.
  `lib/api/generated.ts` is auto-generated from the backend's OpenAPI spec —
  CI fails if it drifts.

## Running it

```sh
# backend
cd api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your DEEPGRAM_API_KEY
uvicorn main:app --host 0.0.0.0 --port 8000

# mobile
cd app-mobile
npm install
npm start              # scan the QR with Expo Go, or press i for the iOS simulator
```

The app reads the backend URL from `EXPO_PUBLIC_API_URL` (defaults to the Expo
dev-server host, which works for both simulator and a phone on the same LAN).
