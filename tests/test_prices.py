import pytest
from unittest.mock import patch, MagicMock
from models.crypto_price import CryptoPrice
from extensions_file import db, cache

# --- Tests for Price Routes (using mocks and auth) ---
def test_get_crypto_prices_success(client, auth_headers, app, mock_coin_gecko_response):
    with patch('routes.prices.fetch_crypto_data', return_value=mock_coin_gecko_response):
        cache.clear()
        response = client.get('/api/prices', headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()
    assert 'prices' in data
    assert 'data_last_updated' in data
    assert 'fetched_at' in data

    prices = data['prices']
    assert 'bitcoin' in prices
    assert prices['bitcoin']['name'] == 'Bitcoin'
    assert prices['bitcoin']['symbol'] == 'BTC'
    assert prices['bitcoin']['price_usd'] == pytest.approx(65000.12)

    assert 'ethereum' in prices
    assert prices['ethereum']['name'] == 'Ethereum'
    assert prices['ethereum']['symbol'] == 'ETH'
    assert prices['ethereum']['price_usd'] == pytest.approx(3500.45)


def test_get_crypto_prices_unauthorized(client):
    cache.clear()
    response = client.get('/api/prices')

    assert response.status_code == 401


# --- FIX 3: Apply the same patching fix here ---
def test_get_crypto_prices_fallback_to_db(client, auth_headers, app):
    with app.app_context():
        db.session.query(CryptoPrice).filter(CryptoPrice.coin_id.in_(['bitcoin', 'ethereum', 'binancecoin', 'solana'])).delete(synchronize_session=False)

        cached_btc = CryptoPrice()
        cached_btc.coin_id = 'bitcoin'
        cached_btc.name = 'Bitcoin'
        cached_btc.symbol = 'BTC'
        cached_btc.price_usd = 64000.00
        cached_btc.price_change_24h = 0.5
        db.session.add(cached_btc)
        db.session.commit()

    with patch('routes.prices.fetch_crypto_data', return_value=[]): # Mock failure in the route
        cache.clear()
        response = client.get('/api/prices', headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()
    prices = data['prices']

    assert 'bitcoin' in prices
    assert prices['bitcoin']['name'] == 'Bitcoin'
    assert prices['bitcoin']['symbol'] == 'BTC'
    assert prices['bitcoin']['price_usd'] == pytest.approx(64000.00)


