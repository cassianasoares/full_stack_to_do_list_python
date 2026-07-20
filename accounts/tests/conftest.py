from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Return a fresh DRF APIClient for each test."""
    return APIClient()


@pytest.fixture
def register_url() -> str:
    from django.urls import reverse
    return reverse('accounts:register')


@pytest.fixture
def login_url() -> str:
    from django.urls import reverse
    return reverse('accounts:login')


@pytest.fixture
def user_payload():
    return {
        "first_name": "Lucas",
        "last_name": "Silva",
        "username": "lucassilva",
        "role": "Dev",
        "email": "lucas@example.com",
        "password": "senha_forte_123",
        "password_confirm": "senha_forte_123",
    }

@pytest.fixture
def existing_user(user_payload):
    return User.objects.create_user(
        email=user_payload["email"],
        password=user_payload["password"],
        first_name=user_payload["first_name"],
        last_name=user_payload["last_name"],
        username=user_payload["username"],
        role=user_payload["role"],
    )
