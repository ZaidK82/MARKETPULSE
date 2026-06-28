# MarketPulse Deployment Notes

## Recommended Free Deployment Setup

Use the backend with GitHub Actions cron.

```txt
GitHub Actions cron
↓
Deployed backend
↓
POST /api/v1/scheduler/run-once
↓
Discord notification if alert is triggered