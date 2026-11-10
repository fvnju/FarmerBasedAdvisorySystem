"""Test set-up. Each test gets a new in-memory SQLite database with foreign keys on, like MySQL.

The tests do not use the MySQL database in .env.
"""

import os

os.environ["DATABASE_URL"] = "sqlite://"  # Set before app.database is imported. load_dotenv does not replace it.
os.environ["JWT_SECRET"] = "test-secret-that-is-long-enough-for-hs256-0123456789"
os.environ["SEED_ADMIN_PASSWORD"] = "admin-password-1"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool

import app.database as database

engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)  # One shared connection, so all sessions see the same in-memory database


@event.listens_for(engine, "connect")
def _foreign_keys_on(connection, _record):  # SQLite does not check foreign keys unless told to
    connection.execute("PRAGMA foreign_keys=ON")


database.engine = engine
database.SessionLocal.configure(bind=engine)

import app.model  # noqa: E402  Register all tables
from app.integration.notifier import get_notifier  # noqa: E402
from app.main import app  # noqa: E402

API = "/api/v1"
ADMIN_PASSWORD = os.environ["SEED_ADMIN_PASSWORD"]
PASSWORD = "secret123"


class Api:  # Small wrapper that adds the /api/v1 prefix and the access token
    def __init__(self, client: TestClient, token: str | None = None):
        self.client = client
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    def get(self, path, **params):
        return self.client.get(API + path, params=params, headers=self.headers)

    def post(self, path, json=None):
        return self.client.post(API + path, json=json, headers=self.headers)

    def patch(self, path, json):
        return self.client.patch(API + path, json=json, headers=self.headers)

    def delete(self, path, **params):
        return self.client.delete(API + path, params=params, headers=self.headers)


def created(response):  # Return the body of a 201 response
    assert response.status_code == 201, response.json()
    return response.json()


def login(client: TestClient, username: str, password: str = PASSWORD) -> dict:  # Return the token pair
    response = client.post(f"{API}/auth/login", json={"login": username, "password": password})
    assert response.status_code == 200, response.json()
    return response.json()


@pytest.fixture
def client():
    database.Base.metadata.create_all(engine)
    get_notifier().outbox.clear()
    test_client = TestClient(app)  # Not used as a context manager, so the start-up migrations do not run
    assert test_client.post("/seed-data").status_code == 200  # Open, because no user exists yet
    yield test_client
    database.Base.metadata.drop_all(engine)


@pytest.fixture
def empty_client():  # Tables without seed data, as after the first migration
    database.Base.metadata.create_all(engine)
    yield TestClient(app)
    database.Base.metadata.drop_all(engine)


@pytest.fixture
def anonymous(client):
    return Api(client)


@pytest.fixture
def api(client):  # Logged in as the seeded admin
    return Api(client, login(client, "johndoe", ADMIN_PASSWORD)["access_token"])


@pytest.fixture
def make_user(client, api):  # Create a user with a role, log in, and return (user, Api)
    roles = {role["name"]: role["id"] for role in api.get("/roles").json()["items"]}

    def make(username: str, role: str):
        user = created(api.post("/users", {
            "username": username, "email": f"{username}@farm.ng", "password": PASSWORD,
            "role_ids": [roles[role]],
        }))
        return user, Api(client, login(client, username)["access_token"])

    return make


@pytest.fixture
def world(api):  # A farmer, an agent, a farm, a crop, and a crop cycle
    roles = api.get("/roles", q="farmer").json()["items"]  # Also finds extension_agent, whose description has "farmers"
    farmer_role = next(role for role in roles if role["name"] == "farmer")
    farmer = created(api.post("/users", {
        "username": "amina", "email": "amina@farm.ng", "password": PASSWORD, "role_ids": [farmer_role["id"]],
    }))
    agent = created(api.post("/users", {"username": "bello", "email": "bello@farm.ng", "password": PASSWORD}))
    admin = api.get("/users", q="johndoe").json()["items"][0]
    region = created(api.post("/regions", {"name": "Guinea Savanna", "is_supported": True}))
    crop = created(api.post("/crops", {"name": "Maize", "scientific_name": "Zea mays", "is_supported": True}))
    farm = created(api.post("/farms", {
        "owner_id": farmer["id"], "region_id": region["id"], "name": "Kuje plot",
        "budget_min": 5000, "budget_max": 20000,
    }))
    cycle = created(api.post("/crop-cycles", {
        "farm_id": farm["id"], "crop_id": crop["id"], "crop_stage": "vegetative", "planting_date": "2026-06-01",
    }))
    return {"farmer": farmer, "agent": agent, "admin": admin, "farmer_role": farmer_role,
            "region": region, "crop": crop, "farm": farm, "cycle": cycle}
