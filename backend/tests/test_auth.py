import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import User

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    db = SessionLocal()
    try:
        db.query(User).filter(User.email.like("%@test.com")).delete()
        db.commit()
    finally:
        db.close()

    yield

    db = SessionLocal()
    try:
        db.query(User).filter(User.email.like("%@test.com")).delete()
        db.commit() 
    finally:
        db.close()


# REGISTRATION TEST

def test_register():
    response = client.post(
        "/v1/register",
        json = {
            "username":"Nien",
            "email": "nien@test.com",
            "password":"nien",
            "role":"User"
        }
    )

    # First Assert the response
    assert response.status_code == 200

    # get the data and parse into JSON
    data = response.json()

    # assert the supposed results
    assert data["username"] == "Nien"
    assert data["email"] == "nien@test.com"
    assert "id" in data


# TODO: Test Cases
# duplicate_register
def test_duplicate_registration():
   client.post(
        "/v1/register",
        json = {
            "username":"jiyeon",
            "email": "jiyeon@test.com",
            "password":"nien",
            "role":"User"
        }
    )
   
   response_user2 = client.post(
        "/v1/register",
        json={
            "username":"Nien12",
            "email": "jiyeon@test.com",
            "password":"nien",
            "role":"User"
        }
    )
   assert response_user2.status_code == 400
   assert response_user2.json()["detail"] == "User already exists."


# login
def test_login():
    client.post(
        "/v1/register",
        json={
            "username":"Naky",
            "email": "naky@test.com",
            "password":"naky",
            "role":"Admin"
        }
    )

    login_response = client.post(
        "/v1/login",
        data = {
            "username":"naky@test.com",
            "password":"naky"
        }
    )

    assert login_response.status_code == 200
    data = login_response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_invalid_login():
    response = client.post(
        "/v1/login",
        data = {
            "username":"naky@test.com",
            "password":"12qwer"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect Password."


def test_get_current_user():
    registration_response = client.post(
        "/v1/register",
        json = {
            "username":"Amber",
            "email": "amber@test.com",
            "password":"aysss",
            "role":"User"
        }
    )

    assert registration_response.status_code == 200

    # login

    login_response = client.post(
        "/v1/login",
        data ={
            "username":"amber@test.com",
            "password":"aysss"
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]


    get_response = client.get(
        "/v1/me",
        headers={"Authorization":f"Bearer {token}"}
    )

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["email"] == "amber@test.com" 
    assert data["role"] == "User"

def test_get_current_with_invalid_token():
    response = client.get(
        "/v1/me",
        headers={"Authorization":"Bearer invalidtoken"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Unable to Validate Credentials"


def test_get_current_with_no_token():
    response = client.get(
        "/v1/me"
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


