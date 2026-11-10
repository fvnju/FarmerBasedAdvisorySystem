"""Tests for the CRUD routes: search, pagination, business rules, and delete-all."""

from tests.conftest import Api, created, login


# Routes, search, and pagination


def test_routes_show_only_supported_operations(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert "post" not in paths["/api/v1/audit-logs"]
    assert "delete" not in paths["/api/v1/audit-logs/{item_id}"]
    assert "patch" not in paths["/api/v1/weather-forecasts/{item_id}"]
    assert "patch" not in paths["/api/v1/consent-records/{item_id}"]
    assert "post" not in paths["/api/v1/refresh-tokens"]


def test_search_and_pagination(api):
    for name in ["North Guinea Savanna", "Sudan Savanna", "Derived 50%_Savanna", "Rainforest"]:
        created(api.post("/regions", {"name": name}))

    page = api.get("/regions", q="savanna", size=2).json()
    assert (page["total"], page["pages"], page["has_next"], len(page["items"])) == (3, 2, True, 2)

    assert [r["name"] for r in api.get("/regions", q="50%").json()["items"]] == ["Derived 50%_Savanna"]

    fast = api.get("/regions", include_total=False, size=3).json()
    assert fast["total"] is None and fast["has_next"] is True

    last = api.get("/regions", sort="name", page=2, size=3).json()
    assert [r["name"] for r in last["items"]] == ["Sudan Savanna"] and last["has_next"] is False


def test_query_parameters_are_checked(api):
    assert api.get("/farms", sort="description").status_code == 422
    assert api.get("/farms", colour="red").status_code == 422
    assert api.get("/farms", size=1000).status_code == 422


def test_crud_errors(api, world):
    farm_id = world["farm"]["id"]
    assert api.get("/farms/9999").status_code == 404
    assert api.patch(f"/farms/{farm_id}", {}).status_code == 422
    assert api.patch(f"/farms/{farm_id}", {"name": None}).status_code == 422
    assert api.post("/farms", {"owner_id": 999, "name": "F"}).status_code == 409


# Users and roles


def test_user_password_and_email(api, world):
    farmer = world["farmer"]
    assert "hashed_password" not in farmer and "password" not in farmer
    assert [r["name"] for r in farmer["roles"]] == ["farmer"]
    duplicate = api.post("/users", {"username": "other", "email": "AMINA@farm.ng", "password": "secret123"})
    assert duplicate.status_code == 409
    unknown_role = api.post("/users", {"username": "xyz", "email": "x@a.io", "password": "secret123", "role_ids": [999]})
    assert unknown_role.status_code == 404


def test_system_roles_are_protected(api, world):
    role_id = world["farmer_role"]["id"]
    assert api.delete(f"/roles/{role_id}").status_code == 409
    assert api.patch(f"/roles/{role_id}", {"name": "grower"}).status_code == 409


def test_role_gets_modules_of_its_privileges(api):
    assert api.post("/privileges", {"module_id": 1, "code": "farms.export"}).status_code == 422
    privilege = created(api.post("/privileges", {"module_id": 1, "code": "users.export"}))
    role = created(api.post("/roles", {"name": "viewer", "privilege_ids": [privilege["id"]]}))
    assert [m["id"] for m in role["modules"]] == [1]


# Farms and crop cycles


def test_farm_rules(api, world):
    owner = world["farmer"]["id"]
    assert api.post("/farms", {"owner_id": owner, "name": "F", "budget_min": 10, "budget_max": 5}).status_code == 422
    assert api.post("/farms", {"owner_id": owner, "name": "F", "latitude": 9.0}).status_code == 422
    assert world["farm"]["currency"] == "NGN"


def test_resource_and_soil_rules(api, world):
    farm_id = world["farm"]["id"]
    resource = {"farm_id": farm_id, "resource_type": "input", "name": "Urea", "is_available": True, "quantity": 2}
    assert api.post("/farm-resources", resource).status_code == 422
    created(api.post("/farm-resources", {**resource, "unit": "bag"}))
    soil = {"farm_id": farm_id, "property_name": "ph", "provenance": "lab_test"}
    assert api.post("/soil-records", soil).status_code == 422
    created(api.post("/soil-records", {**soil, "value": 6.2}))


def test_crop_cycle_rules(api, world):
    cycle = world["cycle"]
    assert cycle["stage_updated_at"] is not None and cycle["status"] == "active"
    assert api.patch(f"/crop-cycles/{cycle['id']}", {"status": "completed"}).status_code == 422
    with_end = {"farm_id": world["farm"]["id"], "crop_id": world["crop"]["id"], "ended_on": "2026-01-01"}
    assert api.post("/crop-cycles", with_end).status_code == 422


def test_agent_assignment(api, world):
    agent, farmer = world["agent"]["id"], world["farmer"]["id"]
    assert api.post("/agent-assignments", {"agent_id": agent, "farmer_id": agent}).status_code == 422
    created(api.post("/agent-assignments", {"agent_id": agent, "farmer_id": farmer}))
    assert api.get("/agent-assignments", q="amin", active=True).json()["total"] == 1


# Advisory flow


def make_request(api, world):
    return created(api.post("/advisory-requests", {
        "farmer_id": world["farmer"]["id"], "assisted_by_id": world["agent"]["id"], "access_mode": "assisted",
        "farm_id": world["farm"]["id"], "crop_cycle_id": world["cycle"]["id"],
        "action_type": "fertilizer", "question": "When should I apply urea?",
    }))


def make_response(api, request_id):
    return created(api.post("/advisory-responses", {
        "request_id": request_id, "action": "Apply 1 bag urea", "reason": "V6 stage",
        "affordability": "affordable", "estimated_cost": 18000, "cost_assumptions": "Urea 18000/bag, Oct 2026",
    }))


def test_advisory_request_rules(client, api, world):
    base = {"farmer_id": world["farmer"]["id"], "action_type": "fertilizer", "question": "When?"}
    farmer = Api(client, login(client, "amina")["access_token"])
    assert farmer.post("/advisory-requests", {**base, "access_mode": "assisted"}).status_code == 422
    for_farmer = created(api.post("/advisory-requests", {**base, "access_mode": "independent"}))
    assert for_farmer["access_mode"] == "assisted" and for_farmer["assisted_by_id"] == world["admin"]["id"]
    other_farmer = {**base, "farmer_id": world["agent"]["id"], "access_mode": "independent", "farm_id": world["farm"]["id"]}
    assert api.post("/advisory-requests", other_farmer).status_code == 422
    request = make_request(api, world)
    assert request["status"] == "pending"
    assert api.patch(f"/advisory-requests/{request['id']}", {"status": "referred"}).status_code == 422


def test_response_answers_the_request(api, world):
    request = make_request(api, world)
    no_cost = {"request_id": request["id"], "action": "Apply", "reason": "Stage", "affordability": "affordable"}
    assert api.post("/advisory-responses", no_cost).status_code == 422
    make_response(api, request["id"])
    assert api.get(f"/advisory-requests/{request['id']}").json()["status"] == "answered"


def test_explanations_and_citations(api, world):
    response = make_response(api, make_request(api, world)["id"])
    text = {"response_id": response["id"], "model_name": "gemma", "validation_status": "passed"}
    first = created(api.post("/advisory-explanations", {**text, "text": "Apply now."}))
    second = created(api.post("/advisory-explanations", {**text, "text": "Apply this week."}))
    assert api.get(f"/advisory-explanations/{first['id']}").json()["is_current"] is False

    document = created(api.post("/knowledge-documents", {"title": "Maize guide", "crop_id": world["crop"]["id"]}))
    chunk = created(api.post("/document-chunks", {
        "document_id": document["id"], "chunk_index": 0, "content": "Apply urea at V6.",
        "embedding": [0.1, 0.2], "embedding_model": "e5",
    }))
    assert len(chunk["content_hash"]) == 64 and "embedding" not in chunk
    citation = {"explanation_id": second["id"], "chunk_id": chunk["id"], "rank": 1}
    assert api.post("/advisory-citations", citation).status_code == 422  # Document is a draft

    rejected = api.patch(f"/knowledge-documents/{document['id']}", {"review_status": "rejected"})
    assert rejected.status_code == 422  # A rejection needs a reason
    approved = api.patch(f"/knowledge-documents/{document['id']}", {"review_status": "approved"}).json()
    assert approved["reviewed_by_id"] == world["admin"]["id"]  # The logged-in user is the reviewer
    assert approved["reviewed_at"] is not None
    created(api.post("/advisory-citations", citation))


def test_feedback_and_observation_rules(api, world):
    response = make_response(api, make_request(api, world)["id"])
    assert api.post("/advisory-feedback", {"response_id": response["id"], "outcome": "rejected"}).status_code == 422
    feedback = created(api.post("/advisory-feedback", {
        "response_id": response["id"], "outcome": "followed", "action_date": "2026-10-01",
    }))
    observation = {"crop_cycle_id": world["cycle"]["id"], "observation": "Leaves greener"}
    assert api.post("/field-observations", {**observation, "observed_on": "2099-01-01"}).status_code == 422
    saved = created(api.post("/field-observations", {
        **observation, "observed_on": "2026-10-10", "feedback_id": feedback["id"],
    }))
    verified = api.patch(f"/field-observations/{saved['id']}", {"is_verified": True}).json()
    assert verified["verified_by_id"] == world["admin"]["id"]  # The logged-in user is the verifier
    unverified = api.patch(f"/field-observations/{saved['id']}", {"is_verified": False}).json()
    assert unverified["verified_by_id"] is None


# Weather, prices, alerts, audit


def test_weather_pages_are_small(api):
    failed = {"provider": "om", "latitude": 9, "longitude": 7, "status": "failed"}
    assert api.post("/weather-forecasts", failed).status_code == 422
    forecast = created(api.post("/weather-forecasts", {
        "provider": "open-meteo", "latitude": 9, "longitude": 7, "status": "ok", "payload": {"rain_mm": [3, 0]},
    }))
    assert "payload" not in api.get("/weather-forecasts").json()["items"][0]
    assert api.get(f"/weather-forecasts/{forecast['id']}").json()["payload"] == {"rain_mm": [3, 0]}
    policy = {"action_type": "irrigation", "requires_forecast": True}
    assert api.post("/freshness-policies", policy).status_code == 422
    created(api.post("/freshness-policies", {**policy, "max_forecast_age_hours": 6}))


def test_price_rules(api):
    price = {"item_name": "urea", "unit": "50 kg bag", "price": 18000, "priced_on": "2026-10-01"}
    assert api.post("/price-records", {**price, "source": "user_quotation"}).status_code == 422
    created(api.post("/price-records", {**price, "source": "market_survey"}))


def test_alert_needs_consent(api, world):
    alert = {
        "user_id": world["farmer"]["id"], "farm_id": world["farm"]["id"], "channel": "sms",
        "title": "Rain", "message": "Heavy rain tomorrow", "dedupe_key": "1:rain:2026-11-11",
        "scheduled_for": "2026-11-11T06:00:00",
    }
    assert api.post("/alerts", alert).status_code == 409
    created(api.post("/consent-records", {
        "user_id": world["farmer"]["id"], "consent_type": "alerts", "granted": True, "policy_version": "1.0",
    }))
    saved = created(api.post("/alerts", alert))
    assert api.post("/alerts", alert).status_code == 409  # Same dedupe_key
    assert api.patch(f"/alerts/{saved['id']}", {"status": "sent"}).json()["sent_at"] is not None
    assert api.get("/alerts", unread=True).json()["total"] == 1


def test_audit_trail_is_read_only(api, world):
    page = api.get("/audit-logs", entity_type="farms", size=5).json()
    assert page["total"] >= 1 and "details" not in page["items"][0]
    assert api.get(f"/audit-logs/{page['items'][0]['id']}").json()["details"] is not None
    assert api.delete("/audit-logs", confirm=True).status_code == 405


# Delete


def test_delete_all_needs_confirm(api):
    assert api.delete("/regions").status_code == 422


def test_delete_all_skips_protected_and_used_records(api, world):
    assert api.delete("/crops", confirm=True).json() == {"deleted": 0, "skipped": 1}  # A crop cycle uses it
    assert api.delete("/roles", confirm=True).json() == {"deleted": 0, "skipped": 4}  # System roles


def test_delete_crop_in_use_gives_clear_message(api, world):
    response = api.delete(f"/crops/{world['crop']['id']}")
    assert response.status_code == 409
    assert "use this record" in response.json()["detail"]


def test_delete_farm_removes_its_children(api, world):
    make_request(api, world)
    created(api.post("/field-observations", {
        "crop_cycle_id": world["cycle"]["id"], "observed_on": "2026-10-10", "observation": "Leaves greener",
    }))
    assert api.delete("/farms", confirm=True).json() == {"deleted": 1, "skipped": 0}
    assert api.get("/crop-cycles").json()["total"] == 0
    assert api.get("/advisory-requests").json()["items"][0]["farm_id"] is None  # SET NULL keeps the request
    deleted = api.get("/audit-logs", action="delete", entity_type="field_observations").json()
    assert deleted["total"] == 1  # The audit trail records the deleted children


def test_delete_user_removes_farms_and_assignments(api, world):
    created(api.post("/agent-assignments", {"agent_id": world["agent"]["id"], "farmer_id": world["farmer"]["id"]}))
    assert api.delete(f"/users/{world['farmer']['id']}").status_code == 204
    assert api.get("/farms").json()["total"] == 0
    assert api.get("/agent-assignments").json()["total"] == 0
