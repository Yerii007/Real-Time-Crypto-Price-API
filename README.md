# Real-Time Crypto Price API

A Flask-based REST API that fetches real-time cryptocurrency prices from the CoinGecko API, stores them in a database, and exposes endpoints to retrieve data. Includes JWT authentication, caching, background updates, and full test coverage.

## 🚀 Features

- User registration & login (JWT authentication)
- Fetch real-time crypto prices (Bitcoin, Ethereum, Binance Coin, Solana by default)
- Fallback to cached DB data if API is unavailable
- Background thread to update DB periodically
- Flask-Caching to speed up responses
- Well-structured modules (services, routes, models)
- Unit and integration tests with Pytest

## 🛠️ Tech Stack

- **Flask** – REST API framework  
- **Flask-JWT-Extended** – Authentication  
- **Flask-SQLAlchemy** – ORM  
- **Flask-Caching** – Caching layer  
- **SQLite** (default) or any SQLAlchemy-compatible DB  
- **Pytest** – Testing framework  

## 📂 Project Structure

```
Real-Time Crypto Price API/
│
├── app.py                # App factory & app setup
├── config.py             # Configuration settings
├── extensions.py         # Centralized extensions (db, cache)
│
├── models/               # SQLAlchemy models
│   ├── user.py
│   └── crypto_price.py
│
├── routes/               # API blueprints
│   ├── auth.py
│   └── prices.py
│
├── services/             # Business logic
│   ├── auth_service.py
│   └── crypto_service.py
│
├── utils/                # Utilities (background updater, helpers)
│   └── background.py
│
├── tests/                # Pytest tests
│   ├── test_auth.py
│   ├── test_models.py
│   └── test_prices.py
│
└── README.md
```

## 🔧 Setup & Installation

1. Clone the repository:

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd Real-Time Crypto Price API
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set environment variables (optional – defaults provided):

```
SECRET_KEY=dev-secret-key
JWT_SECRET_KEY=jwt-secret-key
DATABASE_URL=sqlite:///crypto.db
CACHE_DEFAULT_TIMEOUT=300
UPDATE_INTERVAL=300
```

5. Run the app:

```bash
python app.py
```

## 🧪 Running Tests

```bash
pytest -v
```

## 🔑 API Endpoints

### Auth

- `POST /api/register` – Register new user  
- `POST /api/login` – Login user and get JWT  

### Prices

- `GET /api/prices` – Get real-time crypto prices (JWT required)

## 🐳 Docker (optional)

A `Dockerfile` can be added to containerize the app. (Planned for the next phase.)

## 📜 License

MIT License
