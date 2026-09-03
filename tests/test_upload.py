def test_upload(client):
    client.post("/register", json={"username": "javed", "password": "javed"})
    
    login_response = client.post("/login", data={"username": "javed", "password": "javed"})
    token = login_response.json()["access_token"]

    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

    file = {"file": ("test.txt", b"test file, hello world", "text/plain")}

    response = client.post(
        "/upload/", 
        files=file, 
        headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200