# MarketPulse Backend

FastAPI backend for the MarketPulse stock alert system.

## Run Locally

```bash
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload