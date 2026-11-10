"""Tests for authentication, privileges (RBAC), and the data scope."""

import app.database as database
from app.integration.notifier import get_notifier
from app.service.system import SystemService
from app.seed import MODULES
from app.service.base import BaseService
from tests.conftest import API, PASSWORD, Api, created, login


def last_message():
    return get_notifier().outbox[-1]


# Login, tokens, and sessions


def test_routes_need_a_login(anonymous):
    response = anonymous.get("/farms")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert anonymous.get("/farms", ).json()["detail"].startswith("Log in first")


def test_bad_tokens_are_refused(client):
    for token in ["not-a-jwt", "eyJhbGciOiJub25lIn0.eyJzdWIiOiIxIn0."]:  # The second has algorithm "none"
        assert Api(client, token).get("/farms").status_code == 401


def test_register_and_login(client, anonymous):
    user = created(anonymous.post("/auth/register", {
        "username": "chidi", "email": "Chidi@Farm.NG", "password": PASSWORD, "consents": ["alerts", "location"],
    }))
    assert user["roles"][0]["name"] == "farmer" and "farms.read" in user["privileges"]
    assert last_message().channel == "email" and last_message().address == "chidi@farm.ng"
    tokens = login(client, "CHIDI@farm.ng")  # Email in any letter case
    me = Api(client, tokens["access_token"])
    assert me.get("/auth/me").json()["username"] == "chidi"
    assert me.get("/consent-records").json()["total"] == 2


REGISTER_BODY = {  # The request from the bug report
    "username": "test1", "email": "test1@email.com", "password": "Password123@",
    "phone_number": "+768060084", "full_name": "string", "preferred_language": "en", "consents": ["location"],
}


def test_register_before_seed_gives_clear_error(empty_client):
    response = empty_client.post(f"{API}/auth/register", json=REGISTER_BODY)
    assert response.status_code == 409  # Was a 500 error
    assert "POST /seed-data" in response.json()["detail"]


def test_startup_creates_roles_so_register_works(empty_client):
    db = database.SessionLocal()
    try:
        assert SystemService(db).ensure_rbac() is True
        assert SystemService(db).ensure_rbac() is False  # Roles exist, so no change
    finally:
        db.close()
    response = empty_client.post(f"{API}/auth/register", json=REGISTER_BODY)
    assert response.status_code == 201, response.json()
    assert response.json()["phone_number"] == "+768060084"
    assert empty_client.post("/seed-data").status_code == 200  # Still open: no admin exists yet


def test_failed_logins_lock_the_account(client, world):
    for _ in range(5):
        bad = client.post(f"{API}/auth/login", json={"login": "amina", "password": "wrong-password"})
        assert bad.status_code == 401
    locked = client.post(f"{API}/auth/login", json={"login": "amina", "password": PASSWORD})
    assert locked.status_code == 429
    unknown = client.post(f"{API}/auth/login", json={"login": "nobody", "password": "x"})
    assert unknown.status_code == 401 and unknown.json()["detail"] == bad.json()["detail"]


def test_refresh_rotates_and_detects_reuse(client, world):
    first = login(client, "amina")
    second = client.post(f"{API}/auth/refresh", json={"refresh_token": first["refresh_token"]}).json()
    assert second["refresh_token"] != first["refresh_token"]
    reused = client.post(f"{API}/auth/refresh", json={"refresh_token": first["refresh_token"]})
    assert reused.status_code == 401
    after_reuse = client.post(f"{API}/auth/refresh", json={"refresh_token": second["refresh_token"]})
    assert after_reuse.status_code == 401  # The reuse stopped all sessions


def test_logout(client, world):
    tokens = login(client, "amina")
    assert client.post(f"{API}/auth/logout", json={"refresh_token": tokens["refresh_token"]}).status_code == 204
    assert client.post(f"{API}/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401


def test_sessions_are_listed_for_the_user_only(client, world):
    login(client, "johndoe", "admin-password-1")
    farmer = Api(client, login(client, "amina")["access_token"])
    sessions = farmer.get("/refresh-tokens").json()
    assert sessions["total"] == 1 and sessions["items"][0]["user_id"] == world["farmer"]["id"]


def test_change_password(client, world):
    tokens = login(client, "amina")
    me = Api(client, tokens["access_token"])
    assert me.post("/auth/change-password", {"current_password": "wrong", "new_password": "new-secret-1"}).status_code == 422
    new = me.post("/auth/change-password", {"current_password": PASSWORD, "new_password": "new-secret-1"})
    assert new.status_code == 200
    assert client.post(f"{API}/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401
    login(client, "amina", "new-secret-1")


def test_password_reset(client, anonymous, world):
    assert anonymous.post("/auth/password-reset/request", {"login": "nobody"}).status_code == 202
    assert get_notifier().outbox == []  # Same answer, but no message
    assert anonymous.post("/auth/password-reset/request", {"login": "amina"}).status_code == 202
    token = last_message().token
    reset = {"token": token, "new_password": "reset-secret-1"}
    assert anonymous.post("/auth/password-reset/confirm", reset).status_code == 204
    assert anonymous.post("/auth/password-reset/confirm", reset).status_code == 422  # Used one time only
    login(client, "amina", "reset-secret-1")


def test_email_and_phone_verification(client, world):
    me = Api(client, login(client, "amina")["access_token"])
    assert me.post("/auth/verification/request", {"channel": "phone"}).status_code == 422  # No phone number
    assert me.post("/auth/verification/request", {"channel": "email"}).status_code == 202
    code = last_message().token
    assert me.post("/auth/verification/confirm", {"channel": "email", "code": "wrong"}).status_code == 422
    verified = me.post("/auth/verification/confirm", {"channel": "email", "code": code}).json()
    assert verified["email_verified_at"] is not None
    assert me.post("/auth/verification/request", {"channel": "email"}).status_code == 409

    me.patch("/auth/me", {"phone_number": "+2348012345678"})
    me.post("/auth/verification/request", {"channel": "phone"})
    sms = last_message()
    assert sms.channel == "sms" and sms.token.isdigit() and len(sms.token) == 6
    assert me.post("/auth/verification/confirm", {"channel": "phone", "code": sms.token}).json()["phone_verified_at"]


def test_email_change_needs_new_verification(client, world):
    me = Api(client, login(client, "amina")["access_token"])
    me.post("/auth/verification/request", {"channel": "email"})
    me.post("/auth/verification/confirm", {"channel": "email", "code": last_message().token})
    changed = me.patch("/auth/me", {"email": "amina.new@farm.ng"}).json()
    assert changed["email"] == "amina.new@farm.ng" and changed["email_verified_at"] is None


def test_deactivated_user_is_stopped_at_once(client, api, world):
    farmer = Api(client, login(client, "amina")["access_token"])
    assert farmer.get("/farms").status_code == 200
    api.patch(f"/users/{world['farmer']['id']}", {"is_active": False})
    assert farmer.get("/farms").status_code == 401
    assert client.post(f"{API}/auth/login", json={"login": "amina", "password": PASSWORD}).status_code == 403


# Privileges


def test_every_privilege_in_the_services_is_seeded():
    seeded = {f"{module}.{action}" for module, (_, actions) in MODULES.items() for action in actions}

    def services(cls):
        for sub in cls.__subclasses__():
            yield sub
            yield from services(sub)

    for service in services(BaseService):
        for operation in service.operations:
            assert service.permission_for(operation) in seeded, (service.__name__, operation)


def test_farmer_privileges(make_user):
    _, farmer = make_user("ngozi", "farmer")
    assert farmer.get("/users").status_code == 403
    assert farmer.post("/regions", {"name": "X"}).status_code == 403
    assert farmer.get("/regions").status_code == 200
    assert farmer.delete("/farms", confirm=True).status_code == 403
    assert farmer.get("/audit-logs").status_code == 403
    denied = farmer.get("/roles")
    assert denied.status_code == 403 and denied.json()["errors"]["privilege"] == "rbac.read"


def test_only_admins_assign_roles(make_user, api):
    _, agent = make_user("tunde", "extension_agent")
    admin_role = api.get("/roles", q="admin").json()["items"][0]["id"]
    escalate = {"username": "evil", "email": "evil@farm.ng", "password": PASSWORD, "role_ids": [admin_role]}
    assert agent.post("/users", escalate).status_code == 403


def test_seed_is_protected_after_the_first_user(client, api, make_user):
    assert client.post("/seed-data").status_code == 401
    _, farmer = make_user("kemi", "farmer")
    assert client.post("/seed-data", headers=farmer.headers).status_code == 403
    assert client.post("/seed-data", headers=api.headers).status_code == 200


def test_last_admin_is_protected(api, world):
    admin_id = world["admin"]["id"]
    assert api.delete(f"/users/{admin_id}").status_code == 409  # Own account
    assert api.patch(f"/users/{admin_id}", {"is_active": False}).status_code == 422
    assert api.patch(f"/users/{admin_id}", {"role_ids": []}).status_code == 409


# Data scope


def test_farmer_sees_only_own_data(client, api, world, make_user):
    other, other_api = make_user("musa", "farmer")
    other_farm = created(other_api.post("/farms", {"owner_id": other["id"], "name": "Musa plot"}))
    farmer = Api(client, login(client, "amina")["access_token"])

    assert [f["name"] for f in farmer.get("/farms").json()["items"]] == ["Kuje plot"]
    assert farmer.get(f"/farms/{other_farm['id']}").status_code == 404  # Not 403, so IDs do not leak
    assert farmer.patch(f"/farms/{other_farm['id']}", {"name": "Mine"}).status_code == 404
    assert farmer.post("/farms", {"owner_id": other["id"], "name": "Taken"}).status_code == 403
    assert farmer.patch(f"/farms/{world['farm']['id']}", {"owner_id": other["id"]}).status_code == 403
    resource = {"farm_id": other_farm["id"], "resource_type": "input", "name": "Urea", "is_available": True}
    assert farmer.post("/farm-resources", resource).status_code == 403
    assert api.get("/farms").json()["total"] == 2  # The admin sees all


def test_farmer_cannot_set_who_recorded_data(client, world):
    farmer = Api(client, login(client, "amina")["access_token"])
    price = created(farmer.post("/price-records", {
        "item_name": "urea", "unit": "bag", "price": 18000, "source": "user_quotation",
        "priced_on": "2026-10-01", "farm_id": world["farm"]["id"], "recorded_by_id": world["admin"]["id"],
    }))
    assert price["recorded_by_id"] == world["farmer"]["id"]


def test_quotations_are_private(client, make_user, world):
    farmer = Api(client, login(client, "amina")["access_token"])
    created(farmer.post("/price-records", {
        "item_name": "urea", "unit": "bag", "price": 18000, "source": "user_quotation",
        "priced_on": "2026-10-01", "farm_id": world["farm"]["id"],
    }))
    created(farmer.post("/price-records", {
        "item_name": "urea", "unit": "bag", "price": 17500, "source": "market_survey", "priced_on": "2026-10-01",
    }))
    _, other = make_user("musa", "farmer")
    assert [p["source"] for p in other.get("/price-records").json()["items"]] == ["market_survey"]


def test_agent_registers_and_helps_a_farmer(client, make_user, world):
    agent_user, agent = make_user("tunde", "extension_agent")
    farmer = created(agent.post("/users", {"username": "hauwa", "email": "hauwa@farm.ng", "password": PASSWORD}))
    assert [r["name"] for r in farmer["roles"]] == ["farmer"]
    assert agent.get("/agent-assignments", active=True).json()["items"][0]["farmer_id"] == farmer["id"]

    farm = created(agent.post("/farms", {"owner_id": farmer["id"], "name": "Hauwa plot"}))
    request = created(agent.post("/advisory-requests", {
        "farmer_id": farmer["id"], "access_mode": "independent", "farm_id": farm["id"],
        "action_type": "planting", "question": "When should I plant?",
    }))
    assert request["access_mode"] == "assisted" and request["assisted_by_id"] == agent_user["id"]
    assert agent.get(f"/farms/{world['farm']['id']}").status_code == 404  # Not an assigned farmer

    consent = created(agent.post("/consent-records", {
        "user_id": farmer["id"], "consent_type": "alerts", "granted": True, "policy_version": "1.0",
    }))
    assert consent["recorded_by_id"] == agent_user["id"]


def test_agronomist_sees_all_and_reviews(make_user, world):
    agronomist_user, agronomist = make_user("dr_ade", "agronomist")
    assert agronomist.get(f"/farms/{world['farm']['id']}").status_code == 200
    assert agronomist.post("/farms", {"owner_id": world["farmer"]["id"], "name": "X"}).status_code == 403
    document = created(agronomist.post("/knowledge-documents", {"title": "Maize guide"}))
    assert document["uploaded_by_id"] == agronomist_user["id"]
    approved = agronomist.patch(f"/knowledge-documents/{document['id']}", {"review_status": "approved"}).json()
    assert approved["reviewed_by_id"] == agronomist_user["id"] and approved["reviewed_at"]


def test_farmer_marks_alert_as_read_only(client, api, world):
    created(api.post("/consent-records", {
        "user_id": world["farmer"]["id"], "consent_type": "alerts", "granted": True, "policy_version": "1.0",
    }))
    alert = created(api.post("/alerts", {
        "user_id": world["farmer"]["id"], "channel": "in_app", "title": "Rain", "message": "Heavy rain",
        "dedupe_key": "rain-1", "scheduled_for": "2026-11-11T06:00:00",
    }))
    farmer = Api(client, login(client, "amina")["access_token"])
    assert farmer.patch(f"/alerts/{alert['id']}", {"read_at": "2026-11-11T07:00:00"}).status_code == 200
    assert farmer.patch(f"/alerts/{alert['id']}", {"title": "Changed"}).status_code == 403


def test_audit_trail_records_the_user(api, world):
    page = api.get("/audit-logs", entity_type="farms", action="insert").json()
    assert page["items"][0]["user_id"] == world["admin"]["id"]
    logins = api.get("/audit-logs", action="auth.login").json()
    assert logins["total"] >= 1


def test_health(client):
    assert client.get("/health").json() == {"status": "ok", "database": "ok"}


def test_seed_refuses_a_non_admin_with_the_admin_name(empty_client):
    db = database.SessionLocal()
    try:
        SystemService(db).ensure_rbac()
    finally:
        db.close()
    created(Api(empty_client).post("/auth/register", {**REGISTER_BODY, "username": "johndoe"}))
    response = empty_client.post("/seed-data")
    assert response.status_code == 409 and "johndoe" in response.json()["detail"]
