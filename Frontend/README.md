# Vendor Selection — React Chat UI

Simple chat interface for the Vendor Selection backend.

## Run (development)

**Terminal 1 — Backend**

```powershell
cd Backend
.\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

**Terminal 2 — Frontend**

```powershell
cd Frontend
npm install
npm run dev
```

Open http://localhost:3000

The Vite dev server proxies `/api` to `http://localhost:8000`.

## API used

- `POST /api/v1/chat` — body: `{ "message": "...", "session_id": "..." }`

## Build for production

```powershell
npm run build
npm run preview
```

Set `VITE_API_URL` if the API is on a different host (e.g. `http://localhost:8000/api/v1`).
