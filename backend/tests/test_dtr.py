import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import User, DTR, SyncLogs
from datetime import date, datetime

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    db = SessionLocal()
    try:

        db.query(SyncLogs).delete()
        db.query(DTR).filter(
            DTR.user_id.in_(
                db.query(User.id).filter(User.email.like("%@test.com"))
            )
        ).delete(synchronize_session=False)
        db.query(User).filter(User.email.like("%@test.com")).delete()

        db.commit()
    finally:
        db.close()

    yield

    db = SessionLocal()
    try:
        db.query(SyncLogs).delete()
        db.query(DTR).filter(
                   DTR.user_id.in_(
                       db.query(User.id).filter(User.email.like("%@test.com"))
                   )
               ).delete(synchronize_session=False)
               
        db.query(User).filter(User.email.like("%@test.com")).delete()
        db.commit() 
    finally:
        db.close()


def test_time_in():

    client.post(
        "/v1/register",
        json={
            "username":"Naky",
            "email": "naky@test.com",
            "password":"naky",
            "role":"Admin"
        }
    )

    user_login = client.post(
        "/v1/login",
        data={
            "username":"naky@test.com",
            "password":"naky",
        }
    )

    assert user_login.status_code == 200

    token = user_login.json()["access_token"]

    dtr = client.post(
        "/v1/dtr/time-in",
        json={
            "shift_type":"Full Day (8 Hours)"
        },
        headers={
            "Authorization":f"Bearer {token}"
        }
    )

    assert dtr.status_code == 201


def test_sync_create_logs():
    register_user = client.post(
        "/v1/register",
        json={
            "username": "ihwa",
            "email": "ihwa@test.com",
            "password": "ihwa",
            "role": "User",
        }
    )

    assert register_user.status_code == 200
    user_id = register_user.json()["id"]

    login_user = client.post(
        "/v1/login",
        data={
            "username":"ihwa@test.com",
            "password":"ihwa"
        }
    )

    assert login_user.status_code == 200
    token = login_user.json()["access_token"]

    # actual test

    user_event_id = str(uuid.uuid4())


    event = {
        "user_event_id": user_event_id,
        "user_id": user_id,
        "event_type": "TIME_IN",
        "payload": {
            "shift_type": "Full Day (8 Hours)",
            "timestamp": datetime.now().isoformat(),
        },
        "created_at": datetime.now().isoformat(),
    }

    sync_response = client.post(
        "/v1/dtr/sync",
        json=event,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert sync_response.status_code == 200
    assert sync_response.json()["status"] == "PROCESSED"


def test_sync_time_out():

    register_user = client.post(
            "/v1/register",
            json={
                "username": "ihwo",
                "email": "ihwo@test.com",
                "password": "ihwa",
                "role": "User",
            }
        )
    assert register_user.status_code == 200
    user_id = register_user.json()["id"]
    
    login_user = client.post(
        "/v1/login",
        data={
              "username":"ihwo@test.com",
            "password":"ihwa"
        }
     )
    
    assert login_user.status_code == 200
    token = login_user.json()["access_token"]
    
    # actual test
    
    time_in_event = {
        "user_event_id": str(uuid.uuid4()),
        "user_id": user_id,
        "event_type": "TIME_IN",
        "payload": {
            "shift_type": "Full Day (8 Hours)",
            "timestamp": datetime.now().isoformat(),
        },
        "created_at": datetime.now().isoformat(),
    }

    sync_response1 = client.post(
        "/v1/dtr/sync",
        json=time_in_event,
        headers={"Authorization":f"Bearer {token}"}
    )

    assert sync_response1.status_code == 200
    assert sync_response1.json()["status"] == "PROCESSED"

    time_out_event = {
        "user_event_id": str(uuid.uuid4()),
        "user_id": user_id,
        "event_type": "TIME_OUT",
        "payload": {
            "timestamp": datetime.now().isoformat(),
        },
        "created_at": datetime.now().isoformat(),
    }

    sync_response2 = client.post(
            "/v1/dtr/sync",
            json=time_out_event,
            headers={"Authorization":f"Bearer {token}"}
    )

    assert sync_response2.status_code == 200
    assert sync_response2.json()["status"] == "PROCESSED"


def test_sync_time_out_without_prior_time_in():
    # register
    register_response = client.post(
        "/v1/register",
        json={
            "username": "sync_noin",
            "email": "sync_noin@test.com",
            "password": "testpass",
            "role": "User",
        },
    )
    user_id = register_response.json()["id"]

    # login
    login_response = client.post(
        "/v1/login",
        data={
            "username": "sync_noin@test.com",
            "password": "testpass",
        },
    )
    token = login_response.json()["access_token"]

    # TIME_OUT only — no prior TIME_IN
    event = {
        "user_event_id": str(uuid.uuid4()),
        "user_id": user_id,
        "event_type": "TIME_OUT",
        "payload": {
            "timestamp": datetime.now().isoformat(),
        },
        "created_at": datetime.now().isoformat(),
    }
    response = client.post(
        "/v1/dtr/sync",
        json=event,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400


def test_sync_user_id_mismatch():
    # register user A
    register_a = client.post(
        "/v1/register",
        json={
            "username": "sync_a",
            "email": "sync_a@test.com",
            "password": "testpass",
            "role": "User",
        },
    )

    # register user B
    register_b = client.post(
        "/v1/register",
        json={
            "username": "sync_b",
            "email": "sync_b@test.com",
            "password": "testpass",
            "role": "User",
        },
    )
    user_b_id = register_b.json()["id"]

    # log in as user A
    login_a = client.post(
        "/v1/login",
        data={
            "username": "sync_a@test.com",
            "password": "testpass",
        },
    )
    token_a = login_a.json()["access_token"]

    # event claims to belong to user B, but token is user A's
    event = {
        "user_event_id": str(uuid.uuid4()),
        "user_id": user_b_id,
        "event_type": "TIME_IN",
        "payload": {
            "shift_type": "Full Day (8 Hours)",
            "timestamp": datetime.now().isoformat(),
        },
        "created_at": datetime.now().isoformat(),
    }
    response = client.post(
        "/v1/dtr/sync",
        json=event,
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert response.status_code == 403


def test_sync_without_auth():
    event = {
        "user_event_id": str(uuid.uuid4()),
        "user_id": 1,
        "event_type": "TIME_IN",
        "payload": {
            "shift_type": "Full Day (8 Hours)",
            "timestamp": datetime.now().isoformat(),
        },
        "created_at": datetime.now().isoformat(),
    }
    response = client.post("/v1/dtr/sync", json=event)
    assert response.status_code == 401