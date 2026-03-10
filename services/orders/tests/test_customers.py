def test_create_customer(client):
    r = client.post("/customers", json={"email": "new.person@example.com", "name": "New Person", "country": "de"})
    assert r.status_code == 201
    assert r.json()["country"] == "DE"


def test_duplicate_email_is_rejected(client):
    r = client.post("/customers", json={"email": "aiko.tanaka@example.com", "name": "Aiko T", "country": "JP"})
    assert r.status_code == 409


def test_invalid_email_is_rejected(client):
    r = client.post("/customers", json={"email": "not-an-email", "name": "X", "country": "GB"})
    assert r.status_code == 422
