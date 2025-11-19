# React + Vite Frontend

A clean React + MUI dashboard for the Telegram Jobs backend.

## Dev setup

```bash
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:5173
- API proxied to Flask at http://localhost:7000 via Vite proxy (see `vite.config.js`).

If your backend runs on a different host/port, update the proxy target or set:

```bash
# .env.development
VITE_API_BASE=/api
```

## Build

```bash
npm run build
npm run preview
```

## Pages
- Dashboard: stats + 30-day chart
- Best Jobs: curated, scored list
- Messages: tabs (Tech, Non-Tech, Freelance, Fresher)
- Fresher Analysis: experience breakdown chart
- By Date: filter messages by date and type
- Groups by Date: groups joined per day

## Tech
- React 18, Vite
- MUI 6, Emotion
- Recharts
- React Router v6


