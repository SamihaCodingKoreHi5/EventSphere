from fastapi import status


def test_register_user(client):
    """Test successful user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@test.com",
            "password": "strongpassword",
            "full_name": "New User",
            "role": "User"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client, test_user):
    """Test register fails with duplicate email address."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,
            "password": "anotherpassword",
            "full_name": "Duplicate User"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "exists" in response.json()["detail"]


def test_login_success(client, test_user):
    """Test successful token login using form parameters."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "password"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["email"] == test_user.email
    assert data["role"] == test_user.role


def test_login_invalid_password(client, test_user):
    """Test login fails with incorrect credentials."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_me_profile(client, user_headers, test_user):
    """Test fetching profile of authenticated user."""
    response = client.get("/api/v1/auth/me", headers=user_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name
