"""Tests for the registration and login API endpoints."""
from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


# --- Register ---------------------------------------------------------------

@pytest.mark.django_db
def test_register_creates_user_and_returns_201(api_client: APIClient, register_url: str):
    payload = {
        'first_name': 'Carlos',
        'last_name': 'Souza',
        'username': 'carlossouza',
        'role': 'Gerente',
        'email': 'carlos@example.com',
        'password': 'senha_forte_123',
        'password_match': 'senha_forte_123',
    }

    response = api_client.post(register_url, payload, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email='carlos@example.com').exists()


@pytest.mark.django_db
def test_register_without_role_succeeds(api_client: APIClient, register_url: str):
    payload = {
        'first_name': 'Carlos',
        'last_name': 'Souza',
        'username': 'carlossouza2',
        'email': 'carlos_sem_role@example.com',
        'password': 'senha_forte_123',
        'password_match': 'senha_forte_123',
    }

    response = api_client.post(register_url, payload, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email='carlos_sem_role@example.com').exists()
    assert response.data['role'] is None or response.data['role'] == ''


@pytest.mark.django_db
def test_register_returns_user_data_without_password(api_client: APIClient, register_url: str):
    payload = {
        'first_name': 'Ana',
        'last_name': 'Lima',
        'username': 'analima',
        'role': 'Analista',
        'email': 'ana@example.com',
        'password': 'outra_senha_123',
        'password_match': 'outra_senha_123',
    }

    response = api_client.post(register_url, payload, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert 'email' in response.data
    assert 'first_name' in response.data
    assert 'last_name' in response.data
    assert 'role' in response.data
    assert 'password' not in response.data


@pytest.mark.django_db
def test_register_rejects_duplicate_email(api_client: APIClient, register_url: str, existing_user):
    response = api_client.post(
        register_url,
        {
            'first_name': 'Outro',
            'last_name': 'Carlos',
            'username': 'outrocarlos',
            'role': 'Dev',
            'email': existing_user.email,  # mesmo email
            'password': 'outra_senha_123',
            'password_match': 'outra_senha_123',
        },
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_rejects_missing_fields(api_client: APIClient, register_url: str):
    response = api_client.post(register_url, {'first_name': 'Sem Email'}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_rejects_weak_password(api_client: APIClient, register_url: str):
    response = api_client.post(
        register_url,
        {
            'first_name': 'Pedro',
            'last_name': 'Silva',
            'username': 'pedrosilva',
            'role': 'Dev',
            'email': 'pedro@example.com',
            'password': '123',
            'password_match': '123',
        },
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# --- Login ------------------------------------------------------------------

@pytest.mark.django_db
def test_login_with_valid_credentials_returns_200(api_client: APIClient, login_url: str, existing_user, user_payload):
    response = api_client.post(
        login_url,
        {'email': user_payload['email'], 'password': user_payload['password']},
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert 'user' in response.data
    assert 'access' in response.data
    assert 'refresh' in response.data
    assert response.data['user']['email'] == user_payload['email']


@pytest.mark.django_db
def test_login_with_invalid_password_returns_401(api_client: APIClient, login_url: str, existing_user, user_payload):
    response = api_client.post(
        login_url,
        {'email': user_payload['email'], 'password': 'senha_errada'},
        format='json',
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'detail' in response.data
    assert response.data['detail'] == 'Invalid credentials.'


@pytest.mark.django_db
def test_login_with_unknown_email_returns_401(api_client: APIClient, login_url: str):
    response = api_client.post(
        login_url,
        {'email': 'nao_existe@example.com', 'password': 'qualquer_123'},
        format='json',
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'detail' in response.data
    assert response.data['detail'] == 'Invalid credentials.'
