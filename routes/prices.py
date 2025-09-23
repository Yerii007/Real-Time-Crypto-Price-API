from ast import stmt
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from extensions_file import cache 
from services.crypto_service import fetch_crypto_data
from models.crypto_price import CryptoPrice
from models.user import db
from datetime import datetime, timezone
from dateutil import parser
from sqlalchemy import select  

prices_bp = Blueprint("prices", __name__)


@prices_bp.route("/api/prices", methods=["GET"])
@jwt_required()
@cache.cached(timeout=300) 
def get_crypto_prices():
    data = fetch_crypto_data()
    prices = {}
    global_timestamp = datetime.now(timezone.utc)

    if data:
        api_timestamps = []
        for item in data:
            try:
                last_updated = parser.isoparse(item["last_updated"]).replace(tzinfo=None)
                api_timestamps.append(last_updated)
                prices[item["id"]] = {
                    "name": item["name"],
                    "symbol": item["symbol"].upper(),
                    "price_usd": item["current_price"],
                    "price_change_24h_percent": round(item["price_change_percentage_24h"], 2),
                    "last_updated": last_updated.isoformat()
                }
            except Exception as e:
                print(f"Error parsing {item.get('id')}: {e}")
        if api_timestamps:
            global_timestamp = max(api_timestamps)

    required_coins = ["bitcoin", "ethereum", "binancecoin", "solana"]
    for coin in required_coins:
        if coin not in prices:
            stmt = select(CryptoPrice).where(CryptoPrice.coin_id == coin).order_by(CryptoPrice.timestamp.desc())
            latest = db.session.execute(stmt).scalars().first()
            if latest:
                prices[coin] = {
                    "name": latest.name,
                    "symbol": latest.symbol,
                    "price_usd": latest.price_usd,
                    "price_change_24h_percent": round(latest.price_change_24h, 2) if latest.price_change_24h else None,
                    "last_updated": latest.timestamp.isoformat(),
                    "source": "cached"
                }
            else:
                prices[coin] = {
                    "name": coin.capitalize(),
                    "symbol": "N/A",
                    "price_usd": None,
                    "price_change_24h_percent": None,
                    "last_updated": None,
                    "source": "unavailable"
                }

    return jsonify({
        "prices": prices,
        "data_last_updated": global_timestamp.isoformat(),
        "fetched_at": datetime.now(timezone.utc).isoformat()
    })
