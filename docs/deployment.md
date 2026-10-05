# Deployment Guide — Frontend, Backend & Local Agent

## 1. Vercel Deployment (Frontend Web Application)
GreenLedger is optimized for zero-config Vercel deployment:
1. Connect your GitHub repository to Vercel.
2. Ensure Root Directory is set to project root with `vercel.json` or `frontend/`.
3. Set Environment Variables:
   - `NEXT_PUBLIC_LOCAL_AGENT_URL=http://127.0.0.1:8765`
   - `NEXT_PUBLIC_API_URL=https://your-fastapi-backend.com`
4. Deploy the frontend. Real Windows telemetry and optimization actions still require the local agent.

---

## 2. Running FastAPI Backend
```powershell
pip install -r backend/requirements.txt
python backend/main.py
```
Backend runs on `http://127.0.0.1:8000`.

---

## 3. Running Windows Telemetry Agent
```powershell
pip install -r agent/requirements.txt
python agent/api.py
```
Agent listens on `http://127.0.0.1:8765`.

