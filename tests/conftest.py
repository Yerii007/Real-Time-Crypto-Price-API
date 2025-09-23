import pytest
import tempfile
import os
import uuid
from extensions_file import db, cache
from app import create_app
from models.user import User

@pytest.fixture(scope='session')
def app():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SECRET_KEY': 'test-secret-key-for-crypto-api',
        'JWT_SECRET_KEY': 'test-jwt-secret-key-for-crypto-api',
        'CACHE_TYPE': 'SimpleCache',
        'CACHE_DEFAULT_TIMEOUT': 1,
        'UPDATE_INTERVAL': 999999,
    }
    app = create_app()
    app.config.update(test_config)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def sample_user(app):
    unique_id = uuid.uuid4()
    username = f'testuser_{unique_id.hex[:8]}'
    password_plaintext = 'a_strong_test_password_123!'
    user = None
    with app.app_context():
        from services.auth_service import AuthService
        user, token = AuthService.register_user(username, password_plaintext)
        if user is None:
            pytest.fail(f"Failed to create sample user '{username}' in fixture. Check AuthService logic.")
    if user:
        test_password = password_plaintext  # Store password locally if needed for tests
    yield user, token
    with app.app_context():
        user_to_delete = db.session.get(User, user.id) if user else None
        if user_to_delete:
            db.session.delete(user_to_delete)
            db.session.commit()

@pytest.fixture(scope='function')
def auth_headers(sample_user):
    user, token = sample_user
    if token:
        return {'Authorization': f'Bearer {token}'}
    pytest.fail("auth_headers fixture received (None, None) from sample_user fixture.")

@pytest.fixture(autouse=True)
def mock_background_updater(monkeypatch):
    def mock_start_background_updater(app):
        app.logger.info("Background updater mocked and disabled for testing.")
        pass
    monkeypatch.setattr('utils.background.start_background_updater', mock_start_background_updater)

@pytest.fixture
def mock_coin_gecko_response():
    return [
        {
            "id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "image": "...",
            "current_price": 65000.12,
            "market_cap": 1278901234567,
            "market_cap_rank": 1,
            # ... other fields ...
            "price_change_percentage_24h": 1.56084,
            "last_updated": "2023-10-27T10:30:00.123Z" # ISO format string
        },
        {
            "id": "ethereum",
            "symbol": "eth",
            "name": "Ethereum",
            "image": "...",
            "current_price": 3500.45,
            "market_cap": 421098765432,
            "market_cap_rank": 2,
            # ... other fields ...
            "price_change_percentage_24h": -0.7241,
            "last_updated": "2023-10-27T10:30:05.456Z"
        }
        # Add more mock coins if needed for specific tests
    ]
# --- End Fixture for mocking CoinGecko API response ---
