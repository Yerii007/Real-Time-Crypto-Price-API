import pytest
from datetime import datetime, timezone
from models.user import User
from models.crypto_price import CryptoPrice
from extensions_file import db


def test_user_model(app):

    with app.app_context():
        name = 'testuser_model'
        password_plaintext = 'modeltestpasswordSecure123!'
        user = User()
        user.name = name
        user.set_password(password_plaintext)

    # Test attributes
    assert user.name == name
    assert user.password is not None
    assert user.password != password_plaintext

    assert user.check_password(password_plaintext) == True
    assert user.check_password('wrongpassword') == False

    user_dict = user.to_dict()
    assert 'id' in user_dict
    assert user_dict['name'] == name
    assert 'password' not in user_dict

def test_user_model_unique_constraint(app):

    with app.app_context():
        name = 'unique_test_user'
        user1 = User()
        user1.name = name
        user1.set_password('pass1')
        db.session.add(user1)
        db.session.commit()

        user2 = User()
        user2.name = name
        user2.set_password('pass2')
        db.session.add(user2)
    import sqlalchemy.exc
    try:
        db.session.commit()
        assert False, "Should have raised an IntegrityError"
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        users_with_name = db.session.query(User).filter_by(name=name).all()
        assert len(users_with_name) == 1
        assert users_with_name[0].id == user1.id

def test_crypto_price_model(app):

    with app.app_context():
        coin_id = 'testcoin'
        name = 'Test Coin'
        symbol = 'TST'
        price_usd = 123.45
        price_change_24h = -1.23
        timestamp_utc = datetime.now(timezone.utc)
        timestamp_naive = timestamp_utc.replace(tzinfo=None, microsecond=0)

        price = CryptoPrice()
        price.coin_id = coin_id
        price.name = name
        price.symbol = symbol
        price.price_usd = price_usd
        price.price_change_24h = price_change_24h
        price.timestamp = timestamp_naive

        assert price.coin_id == coin_id
        assert price.name == name
        assert price.symbol == symbol
        assert price.price_usd == price_usd
        assert price.price_change_24h == price_change_24h
        assert price.timestamp == timestamp_naive

        price_dict = price.to_dict()
        assert price_dict['coin_id'] == coin_id
        assert price_dict['name'] == name
        assert price_dict['symbol'] == symbol
        assert price_dict['price_usd'] == price_usd
        assert price_dict['price_change_24h'] == price_change_24h
        assert price_dict['timestamp'] == timestamp_naive.isoformat()
        assert 'id' in price_dict


def test_crypto_price_model_timestamp_default(app):

    with app.app_context():
        price = CryptoPrice()
        price.coin_id = 'default_time_coin'
        price.name = 'Default Time Coin'
        price.symbol = 'DTC'
        price.price_usd = 1.00
        db.session.add(price)
        db.session.commit()  

        db.session.refresh(price)
        assert price.timestamp is not None
        now = datetime.now(timezone.utc)
        price_ts = price.timestamp

        if price_ts.tzinfo is None:
            price_ts = price_ts.replace(tzinfo=timezone.utc)

        time_difference = abs((now - price_ts).total_seconds())
        assert time_difference < 5, f"Time difference {time_difference}s is too large. DB timestamp: {price_ts}, Test 'now': {now}"

        price_dict = price.to_dict()
        assert 'timestamp' in price_dict
        assert price_dict['timestamp'] is not None
