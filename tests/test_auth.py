import pytest
from models.user import User
from werkzeug.security import check_password_hash
from extensions_file import db

# --- Tests for POST /api/auth/register ---
def test_register_success(client, app):
    
    new_user_data = {
        'name': 'newuser_register',
        'password': 'SecurePassword123!'
    }
    response = client.post('/api/register', json=new_user_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'User created'
    assert 'access_token' in data
    assert 'user' in data
    assert data['user']['name'] == new_user_data['name']

    with app.app_context():
        user = db.session.get(User, data['user']['id']) # Or query by name
        assert user is not None
        assert user.name == new_user_data['name']
        assert check_password_hash(user.password, new_user_data['password'])


def test_register_missing_fields(client):
    
    response = client.post('/api/register', json={
        'name': 'newuser',
        # Missing password
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'required' in data['error'].lower() # Check for 'required' in message


def test_register_duplicate_username(client, sample_user):
    
    user, _ = sample_user # Get the user object from the fixture
    response = client.post('/api/register', json={
        'name': user.name, # Duplicate
        'password': 'Newpassword123!'
    })
    assert response.status_code == 409 # Conflict
    data = response.get_json()
    assert 'error' in data
    assert 'already exists' in data['error'].lower()


def test_login_success(client, sample_user):
    
    user, _ = sample_user
    response = client.post('/api/login', json={
        'name': user.name,
        'password': user.test_password # Correct password from fixture
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert data['message'] == 'Login successful'
    assert 'access_token' in data
    assert 'user' in data
    assert data['user']['name'] == user.name
    # Optionally verify user ID matches


def test_login_invalid_credentials_username(client, sample_user):
    
    user, _ = sample_user
    response = client.post('/api/login', json={
        'name': 'wrongusername',
        'password': user.test_password
    })
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data
    assert 'invalid credentials' in data['error'].lower()


def test_login_invalid_credentials_password(client, sample_user):
    
    user, _ = sample_user
    response = client.post('/api/login', json={
        'name': user.name,
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data
    assert 'invalid credentials' in data['error'].lower()


def test_login_missing_fields(client):
    
    response = client.post('/api/login', json={
        'name': 'someuser'
        # Missing password
    })
    assert response.status_code in [400, 401]
    data = response.get_json()
    assert 'error' in data
    assert 'missing' in data['error'].lower() or 'required' in data['error'].lower()

