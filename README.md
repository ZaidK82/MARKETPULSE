# MarketPulse — Stock Alert System Backend

MarketPulse is a FastAPI-based stock alert backend that allows users to track stocks, create custom alert rules, evaluate market conditions, and send Discord notifications when bullish or bearish conditions are triggered.

The project is designed as a backend-first portfolio project demonstrating API design, stock market data integration, technical indicator calculation, rule-based alert evaluation, notification delivery, scheduled jobs, and automated cron execution.

---

## Features

### Stock and Watchlist Management

* Add stocks with symbol, name, and exchange
* List tracked stocks
* Add stocks to a watchlist
* Soft-delete watchlist items

### Market Data

* Fetch real-time quote data using `yfinance`
* Fetch historical price data
* Supports configurable period and interval parameters

### Technical Indicators

MarketPulse currently supports:

* SMA — Simple Moving Average
* EMA — Exponential Moving Average
* RSI — Relative Strength Index
* MACD — Moving Average Convergence Divergence

### Alert Rules

Users can create alert rules based on indicators such as:

* `close_price`
* `sma`
* `ema`
* `rsi`
* `macd`
* `macd_signal`
* `macd_histogram`

Supported operators:

* `>`
* `>=`
* `<`
* `<=`
* `==`
* `!=`

Example rule:

```txt
AAPL close_price > 150
```

### Alert Evaluation Engine

The backend evaluates alert rules and creates alert events when conditions are met.

It also includes cooldown protection to prevent duplicate notifications while the same condition remains true.

### Discord Notifications

Triggered alert events can be sent to Discord through a webhook.

The system also stores notification logs for tracking delivery status.

### Scheduler Support

MarketPulse supports two automation modes:

1. Manual run-once scheduler endpoint
2. Optional background APScheduler lifecycle

### GitHub Actions Cron Support

A GitHub Actions workflow can call the deployed backend periodically to trigger alert evaluation.

This is useful for free deployment environments where always-on background workers may not be reliable.

---

## Tech Stack

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* yfinance
* pandas
* APScheduler
* Discord Webhooks
* pytest
* GitHub Actions

---

## Project Structure

```txt
MARKETPULSE/
│
├── .github/
│   └── workflows/
│       └── marketpulse-cron.yml
│
├── docs/
│   └── screenshots/
│
└── marketpulse-backend/
    ├── app/
    │   ├── api/
    │   ├── core/
    │   ├── crud/
    │   ├── models/
    │   ├── schemas/
    │   ├── services/
    │   ├── config.py
    │   └── main.py
    │
    ├── tests/
    ├── .env.example
    ├── pytest.ini
    └── requirements.txt
```

---

## Backend Architecture

```txt
Client / GitHub Actions / Scheduler
        ↓
FastAPI Routes
        ↓
Service Layer
        ↓
CRUD Layer
        ↓
SQLAlchemy Models
        ↓
SQLite Database
```

Market data is fetched through `yfinance`, indicators are calculated in the service layer, alert conditions are evaluated by the alert engine, and notifications are sent through Discord webhooks.

---

## Environment Variables

Create a `.env` file inside `marketpulse-backend/`.

```env
APP_NAME=MarketPulse
APP_ENV=development
APP_VERSION=0.1.0

DATABASE_URL=sqlite:///./marketpulse.db

API_V1_PREFIX=/api/v1

DISCORD_WEBHOOK_URL=

SCHEDULER_ENABLED=false
SCHEDULER_INTERVAL_MINUTES=15

CRON_SECRET=

ALERT_COOLDOWN_MINUTES=60
```

### Variable Reference

| Variable                     | Purpose                                   |
| ---------------------------- | ----------------------------------------- |
| `APP_NAME`                   | Application name                          |
| `APP_ENV`                    | Environment name                          |
| `APP_VERSION`                | API version                               |
| `DATABASE_URL`               | Database connection URL                   |
| `API_V1_PREFIX`              | API route prefix                          |
| `DISCORD_WEBHOOK_URL`        | Discord webhook for notifications         |
| `SCHEDULER_ENABLED`          | Enables background APScheduler            |
| `SCHEDULER_INTERVAL_MINUTES` | Background scheduler interval             |
| `CRON_SECRET`                | Secret used by GitHub Actions cron        |
| `ALERT_COOLDOWN_MINUTES`     | Prevents duplicate alerts during cooldown |

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/ZaidK82/MARKETPULSE.git
cd MARKETPULSE/marketpulse-backend
```

### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate virtual environment

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create `.env`

Copy `.env.example` to `.env` and update values as needed.

### 6. Run the backend

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```txt
http://127.0.0.1:8000
```

Swagger documentation:

```txt
http://127.0.0.1:8000/docs
```

---

## Running Tests

From inside `marketpulse-backend/`:

```bash
pytest
```

Current test status:

```txt
63 passed
```

---

## Main API Endpoints

### Health

| Method | Endpoint               | Description        |
| ------ | ---------------------- | ------------------ |
| GET    | `/api/v1/health`       | Basic health check |
| GET    | `/api/v1/health/ready` | Readiness check    |

### Stocks

| Method | Endpoint                    | Description     |
| ------ | --------------------------- | --------------- |
| POST   | `/api/v1/stocks`            | Create stock    |
| GET    | `/api/v1/stocks`            | List stocks     |
| GET    | `/api/v1/stocks/{stock_id}` | Get stock by ID |

### Watchlist

| Method | Endpoint                                | Description                 |
| ------ | --------------------------------------- | --------------------------- |
| POST   | `/api/v1/watchlist`                     | Add stock to watchlist      |
| GET    | `/api/v1/watchlist`                     | List active watchlist items |
| DELETE | `/api/v1/watchlist/{watchlist_item_id}` | Soft-delete watchlist item  |

### Market Data

| Method | Endpoint                               | Description                 |
| ------ | -------------------------------------- | --------------------------- |
| GET    | `/api/v1/market-data/{symbol}/quote`   | Fetch quote data            |
| GET    | `/api/v1/market-data/{symbol}/history` | Fetch historical price data |

### Indicators

| Method | Endpoint                           | Description    |
| ------ | ---------------------------------- | -------------- |
| GET    | `/api/v1/indicators/{symbol}/sma`  | Calculate SMA  |
| GET    | `/api/v1/indicators/{symbol}/ema`  | Calculate EMA  |
| GET    | `/api/v1/indicators/{symbol}/rsi`  | Calculate RSI  |
| GET    | `/api/v1/indicators/{symbol}/macd` | Calculate MACD |

### Alert Rules

| Method | Endpoint                        | Description            |
| ------ | ------------------------------- | ---------------------- |
| POST   | `/api/v1/alert-rules`           | Create alert rule      |
| GET    | `/api/v1/alert-rules`           | List alert rules       |
| GET    | `/api/v1/alert-rules/{rule_id}` | Get alert rule         |
| PATCH  | `/api/v1/alert-rules/{rule_id}` | Update alert rule      |
| DELETE | `/api/v1/alert-rules/{rule_id}` | Soft-delete alert rule |

### Evaluation

| Method | Endpoint                                            | Description             |
| ------ | --------------------------------------------------- | ----------------------- |
| POST   | `/api/v1/evaluation/alert-rules/{rule_id}/evaluate` | Evaluate one alert rule |

### Notifications

| Method | Endpoint                                                | Description               |
| ------ | ------------------------------------------------------- | ------------------------- |
| POST   | `/api/v1/notifications/alert-events/{event_id}/discord` | Send Discord notification |
| GET    | `/api/v1/notifications/logs`                            | List notification logs    |
| GET    | `/api/v1/notifications/alert-events`                    | List alert events         |

### Scheduler

| Method | Endpoint                     | Description                   |
| ------ | ---------------------------- | ----------------------------- |
| GET    | `/api/v1/scheduler/status`   | Get scheduler status          |
| POST   | `/api/v1/scheduler/run-once` | Run alert evaluation job once |

---

## GitHub Actions Cron

The project includes:

```txt
.github/workflows/marketpulse-cron.yml
```

It can call the deployed backend every 30 minutes:

```txt
POST /api/v1/scheduler/run-once
```

Required GitHub repository secrets:

| Secret                    | Purpose                                          |
| ------------------------- | ------------------------------------------------ |
| `MARKETPULSE_BACKEND_URL` | Base URL of deployed backend                     |
| `CRON_SECRET`             | Secret header used to protect scheduler endpoint |

---

## Deployment Notes

For deployment, configure these environment variables:

```env
DISCORD_WEBHOOK_URL=your_discord_webhook
CRON_SECRET=your_secure_cron_secret
SCHEDULER_ENABLED=false
SCHEDULER_INTERVAL_MINUTES=15
ALERT_COOLDOWN_MINUTES=60
```

Recommended automation mode for free deployments:

```txt
GitHub Actions cron → deployed backend /scheduler/run-once
```

Keep `SCHEDULER_ENABLED=false` when using GitHub Actions cron to avoid duplicate scheduler execution.

---

## Example Alert Flow

```txt
User creates alert rule
        ↓
Scheduler runs
        ↓
Market data is fetched
        ↓
Indicator or price condition is evaluated
        ↓
AlertEvent is created if triggered
        ↓
Cooldown check prevents duplicates
        ↓
Discord notification is sent
        ↓
NotificationLog is stored
```

---

## Current Backend Status

```txt
Completed:
- FastAPI backend foundation
- Database models
- Stock and watchlist APIs
- yfinance market data integration
- Technical indicators
- Alert rule CRUD
- Alert evaluation engine
- Discord notification service
- Scheduler run-once job
- Background scheduler lifecycle
- GitHub Actions cron support
- Duplicate alert cooldown protection
- Test cleanup and pytest configuration
```

---

## Future Improvements

* User authentication
* PostgreSQL support
* Frontend dashboard
* Email or Telegram notifications
* More indicators
* Advanced alert strategies
* Portfolio-based alerts
* Paper trading simulation
* Docker deployment
* Cloud database integration

---

## Disclaimer

This project is for educational and portfolio purposes only. It is not financial advice and should not be used as the sole basis for investment decisions.
