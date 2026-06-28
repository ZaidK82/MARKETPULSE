# MarketPulse Frontend

React + Vite frontend dashboard for the MarketPulse Stock Alert System.

The frontend connects to the FastAPI backend and provides a clean dashboard for managing stocks, watchlists, alert rules, alert history, notification logs, and scheduler execution.

## Tech Stack

- React
- Vite
- Tailwind CSS
- Axios
- React Router
- Lucide React

## Features

- Live backend health dashboard
- Readiness status check
- Stocks and watchlist management
- Quote lookup through backend market data API
- Alert rule creation and management
- Manual alert rule evaluation
- Alert event history
- Discord notification log viewer
- Manual Discord resend action
- Scheduler status dashboard
- Manual scheduler run-once control

## Environment Variables

Create a `.env` file inside `marketpulse-frontend/`.

```env
VITE_API_BASE_URL=http://localhost:8000