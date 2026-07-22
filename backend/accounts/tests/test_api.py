"""Tests for the registration and login API endpoints."""
from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import Task, Category
from rest_framework_simplejwt.tokens import RefreshToken

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
        'password': 'senha_forte_123',  # nosec B105
        'password_match': 'senha_forte_123',  # nosec B105
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
        'password': 'senha_forte_123',  # nosec B105
        'password_match': 'senha_forte_123',  # nosec B105
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
        'password': 'outra_senha_123',  # nosec B105
        'password_match': 'outra_senha_123',  # nosec B105
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
            'email': existing_user.email,
            'password': 'outra_senha_123',  # nosec B105
            'password_match': 'outra_senha_123',  # nosec B105
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
            'password': '123',  # nosec B105
            'password_match': '123',  # nosec B105
        },
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# --- Login ------------------------------------------------------------------

@pytest.mark.django_db
def test_login_with_valid_credentials_returns_200(api_client: APIClient, login_url: str, existing_user, user_payload):
    response = api_client.post(
        login_url,
        {'email': user_payload['email'], 'password': user_payload['password']}, # nosec B105
        format='json',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == user_payload['email']
    assert 'access_token' in response.cookies
    assert 'refresh_token' in response.cookies


@pytest.mark.django_db
def test_login_with_invalid_password_returns_401(api_client: APIClient, login_url: str, existing_user, user_payload):
    response = api_client.post(
        login_url,
        {'email': user_payload['email'], 'password': 'senha_errada'},  # nosec B105
        format='json',
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'detail' in response.data
    assert response.data['detail'] == 'Invalid credentials.'


@pytest.mark.django_db
def test_login_with_unknown_email_returns_401(api_client: APIClient, login_url: str):
    response = api_client.post(
        login_url,
        {'email': 'nao_existe@example.com', 'password': 'qualquer_123'},  # nosec B105
        format='json',
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'detail' in response.data
    assert response.data['detail'] == 'Invalid credentials.'

# --- Me ---------------------------------------------------------------------

@pytest.mark.django_db
def test_me_returns_user_and_tasks(api_client, me_url, existing_user, category):
    task = Task.objects.create(description="Relatório", completed=False, category=category)
    task.responsible.add(existing_user)

    api_client.force_authenticate(user=existing_user)
    response = api_client.get(me_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"]["user"]["email"] == existing_user.email
    assert len(response.data["results"]["tasks"]) == 1
    assert response.data["results"]["tasks"][0]["description"] == "Relatório"


@pytest.mark.django_db
def test_me_filters_tasks_by_category(api_client, me_url, existing_user, category):
    other_category = Category.objects.create(name="Outro")
    task1 = Task.objects.create(description="Task A", completed=False, category=category)
    task2 = Task.objects.create(description="Task B", completed=False, category=other_category)
    task1.responsible.add(existing_user)
    task2.responsible.add(existing_user)

    api_client.force_authenticate(user=existing_user)
    response = api_client.get(f"{me_url}?category={category.id}")

    assert response.status_code == status.HTTP_200_OK
    assert all(t["category"] == category.id for t in response.data["results"]["tasks"])


@pytest.mark.django_db
def test_me_filters_tasks_by_completed(api_client, me_url, existing_user, category):
    task1 = Task.objects.create(description="Task A", completed=True, category=category)
    task2 = Task.objects.create(description="Task B", completed=False, category=category)
    task1.responsible.add(existing_user)
    task2.responsible.add(existing_user)

    api_client.force_authenticate(user=existing_user)
    response = api_client.get(f"{me_url}?completed=true")

    assert response.status_code == status.HTTP_200_OK
    assert all(t["completed"] is True for t in response.data["results"]["tasks"])


# --- Task create ------------------------------------------------------------

@pytest.mark.django_db
def test_create_task_only_description_defaults(api_client, me_tasks_url, existing_user):
    """Only description is mandatory; completed=False, responsible=[user],
        and category defaults to "General" when missing."""
    api_client.force_authenticate(user=existing_user)
    response = api_client.post(me_tasks_url, {'description': 'Estudar DRF'}, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['description'] == 'Estudar DRF'
    assert response.data['completed'] is False
    # User autenticado entra como responsável padrão.
    assert response.data['responsible'] == [existing_user.pk]
    # Categoria default "Geral" foi criada e associada.
    from accounts.models import Category
    geral = Category.objects.get(name='Geral')
    assert response.data['category'] == geral.id


@pytest.mark.django_db
def test_create_task_with_category_and_extra_responsibles(api_client, me_tasks_url, existing_user, category):
    """Other IDs in `responsible` are merged; the authenticated user is not duplicated."""
    other = User.objects.create_user(
        email='maria@example.com', password='senha_forte_123',
        first_name='Maria', last_name='Souza', username='mariasouza',
    )
    another = User.objects.create_user(
        email='joao@example.com', password='senha_forte_123',
        first_name='Joao', last_name='Lima', username='joaolima',
    )

    api_client.force_authenticate(user=existing_user)
    response = api_client.post(
        me_tasks_url,
        {
            'description': 'Planejar sprint',
            'category': category.id,
            'responsible': [other.pk, another.pk],
        },
        format='json',
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['category'] == category.id
    assert response.data['responsible'] == [existing_user.pk, other.pk, another.pk]


@pytest.mark.django_db
def test_create_task_dedups_responsible_and_ignores_self_repeat(
    api_client, me_tasks_url, existing_user
):
    """Duplicates in the payload and the user itself are deduplicated while preserving order."""
    other = User.objects.create_user(
        email='pedro@example.com', password='senha_forte_123',
        first_name='Pedro', last_name='Silva', username='pedrosilva',
    )

    api_client.force_authenticate(user=existing_user)
    response = api_client.post(
        me_tasks_url,
        {
            'description': 'Deduplicar',
            'responsible': [existing_user.pk, other.pk, other.pk],
        },
        format='json',
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['responsible'] == [existing_user.pk, other.pk]


@pytest.mark.django_db
def test_create_task_authenticates_via_bearer(
    api_client, me_tasks_url, existing_user
):
    refresh = RefreshToken.for_user(existing_user)
    access = str(refresh.access_token)

    response = api_client.post(
        me_tasks_url,
        {'description': 'Via bearer'},
        format='json',
        HTTP_AUTHORIZATION=f'Bearer {access}',
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['responsible'] == [existing_user.pk]
