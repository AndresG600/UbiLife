# UbiLife — monorepo

Two independent projects side by side:

- **`Backend/`** — FastAPI + MongoDB (Motor async)
- **`Fronted/`** — Expo SDK 56 (see `Fronted/AGENTS.md` for frontend-specific guidance)

---

## Backend (`Backend/`)

### Run

```bash
cd Backend
# requires .env in Backend/ (copy from .env.docker template was removed; env vars documented in CLAUDE.md)
uvicorn app:app --reload          # dev
uvicorn app:app --host 0.0.0.0    # LAN (what the mobile app expects)
```

### Key facts

- **FastAPI** with lifespan-managed background tasks: MQTT subscriber, GPS watchdog (30s), alert re-send (5min)
- **MongoDB** via `motor` (async). Collections: `Administradores`, `Cuidadores`, `Familiares`, `Pacientes`, `Dispositivos`, `DispositivosDisponibles`, `Historial`, `ZonasSeguras`, `Alertas`, `Grupos`, `Reportes`, `UbicacionesCuidadores`, `UbicacionesFamiliares`, `Invitaciones`, `TokensRevocados`
- **JWT auth** (`PyJWT`, NOT python-jose). Four route dependencies in `security/dependencies.py`: `get_cuidador_actual`, `get_familiar_actual`, `get_cuidador_o_familiar_actual` (adds `_tipo` key), `get_admin_actual` (requires `activo: True`)
- **Rate limiting**: 120 req/60s per IP (in-memory, `security/limiter.py`, respects `TRUST_PROXY` / `X-Forwarded-For`)
- **MQTT** (HiveMQ Cloud): subscribes `ubilife/dispositivo/+/gps`, processes location + alerts
- **Push notifications**: uses **Expo Push API** (`FCM/client.py` — name is misleading), NOT Firebase Admin SDK (`firebase_admin` is installed but unused)
- **SSE** for real-time location: in-memory `EventBus` (`utils/eventos.py`)
- **Sentry** optional via `SENTRY_DSN` env var
- **Field-level encryption**: `services/service_paciente.py` encrypts `enfermedad`, `cedula`, `familiar_telefono` with Fernet; if `FERNET_KEY` unset → no-op passthrough (plaintext)
- **Two MongoDB configs**: main app reads `MONGO_URI` + `DATABASE_NAME` from `os.getenv` (`database/database.py`); MQTT subscriber uses pydantic-settings `MONGODB_URL` + `DATABASE_NAME` (`MQTT/config.py`). Keep both in `.env`.
- **Code in Spanish**: all variables, functions, routes, collection names, comments
- **No tests, no CI/CD** (Procfile exists for Railway, no Docker)

### Architecture pattern

Each module has three layers:
```
routes/ruta_X.py    → FastAPI router (endpoints)
services/service_X.py → Business logic
models/model_X.py   → Pydantic schemas (Base → Create → Response → Update)
```

### Naming gotchas

- `routes/ruta_cliente.py` is the **cuidador** router (misleading filename)
- `FCM/client.py` sends via **Expo Push API**, not Firebase
- Two geo utility files: `utils/geo.py` and `utilidades/geo.py`

### Hardware

`Backend/esp32.ino` — firmware for ESP32-C6-Zero + BZ-251 GPS module. Publishes NMEA-parsed coordinates over MQTT. Not part of build pipeline; flash manually via FTDI232.

---

## Frontend (`Fronted/`)

See `Fronted/AGENTS.md` for detailed SDK 56 quirks, commands, path aliases, and architecture.

Key points not covered there:
- **Map**: Leaflet inside `react-native-webview` (Stadia Maps tiles; API key in `.env`)
- **Notifications**: Expo Push API (not FCM), skips in Expo Go
- **Auth**: token in `expo-secure-store`, user metadata in `AsyncStorage`, auto-logout on 401
- **Styles**: `StyleSheet.create` only — no Tailwind, no styled-components
- **No ESLint config** yet — `npm run lint` runs `expo lint` (no-op until set up)
- **No test framework**

### Commands

| Action | Command |
|---|---|
| Dev server | `npm start` |
| Web | `npm run web` |
| Android | `npm run android` |
| iOS | `npm run ios` |
| Type-check | `npx tsc --noEmit` |
| Lint | `npm run lint` (no-op until configured) |

### Path aliases

- `@/*` → `./src/*`
- `@/assets/*` → `./assets/*`

---

## Cross-cutting

- `Backend/.env` and `Fronted/.env` are **not committed** (each in their own `.gitignore` via `.env*.local` pattern).
- `google-services.json` and `app.json` both use `com.UbiLife.app` — already aligned.
- No pre-commit hooks, no CI workflows.
- Docs UI (`/docs`, `/redoc`) disabled when `ENVIRONMENT=production`.
- `DOCUMENTACION_API.md` (repo root, not tracked) is a hand-written endpoint reference.
