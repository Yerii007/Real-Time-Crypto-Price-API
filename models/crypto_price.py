# models/crypto_price.py
from datetime import datetime, timezone
from extensions_file import db


class CryptoPrice(db.Model):
    __tablename__ = "crypto_prices"
    id = db.Column(db.Integer, primary_key=True)
    coin_id = db.Column(db.String(50), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String(10), nullable=False)
    price_usd = db.Column(db.Float, nullable=False)
    price_change_24h = db.Column(db.Float) # Consider Float or Numeric for precision
    timestamp = db.Column(db.DateTime(timezone=True),
                      default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self):
        """Convert price object to dictionary."""
        return {
            'id': self.id,
            'coin_id': self.coin_id,
            'name': self.name,
            'symbol': self.symbol,
            'price_usd': self.price_usd,
            'price_change_24h': self.price_change_24h,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    def __repr__(self):
        return f"<CryptoPrice {self.name} ({self.symbol}): ${self.price_usd} at {self.timestamp}>"  