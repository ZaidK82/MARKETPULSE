# MarketPulse Backend

MarketPulse is a stock alert system backend built with FastAPI.

## Current Phase

Phase 1: FastAPI backend foundation.

## Features Planned

- User stock watchlist
- Custom bullish and bearish alert rules
- Market data fetching using yfinance
- Technical indicators
- Rule evaluation engine
- Discord webhook alerts
- APScheduler-based local jobs
- GitHub Actions cron support

## Tech Stack

- FastAPI
- SQLite
- SQLAlchemy
- yfinance
- APScheduler
- Discord Webhook
- GitHub Actions

## Setup

```bash
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload