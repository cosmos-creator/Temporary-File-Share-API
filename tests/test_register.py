def test_register(client):
    response = client.post("/register", json={"username": "javed", "password": "javed"})

    assert response.status_code == 200