from datetime import timezone
from flask import current_app
import requests
from dateutil import parser
from extensions_file import db
from models.crypto_price import CryptoPrice
from config import Config
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"

def _requests_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429,500,502,503,504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session

def fetch_crypto_data():
    params = {
        "vs_currency": "usd",
        "ids": Config.COINGECKO_COINS,
        "price_change_percentage": "24h"
    }
    s = _requests_session()
    try:
        resp = s.get(COINGECKO_URL, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as e:
        current_app.logger.warning("HTTP error when calling CoinGecko: %s", e)
        return []
    except Exception as e:
        current_app.logger.exception("Unexpected error fetching CoinGecko data")
        return []

def update_db_with_api_data():
    data = fetch_crypto_data()
    if not data:
        return False

    new_records = []
    for item in data:
        try:
            last_updated_str = item.get("last_updated")
            if last_updated_str:
                last_updated = parser.isoparse(last_updated_str).replace(tzinfo=None, microsecond=0)
            else:
                from datetime import datetime
                last_updated = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)

            record = CryptoPrice(
                crypto_id=item["id"],
                crypto_name=item["name"],
                crypto_symbol=item["symbol"].upper(),
                current_price=item["current_price"],
                price_change_24h=item.get("price_change_percentage_24h"),
                last_updated=last_updated
            )
            db.session.add(record)
            new_records.append(record)
        except Exception as e:
            current_app.logger.error(f"Error parsing/updating {item.get('id', 'Unknown Coin')}: {e}")
            continue

    if new_records:
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Database commit failed: {e}")
            return False
    return False
