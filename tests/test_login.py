def test_login(client):
    response1 = client.post("/register", json={"username": "javed", "password": "javed"})

    assert response1.status_code == 200
    assert "id" in response1.json()

    response2 = client.post("/login", data={"username": "javed", "password": "javed"})

    assert response2.status_code == 200
    assert "access_token" in response2.json()