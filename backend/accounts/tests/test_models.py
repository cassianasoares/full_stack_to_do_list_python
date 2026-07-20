"""Tests for the custom User model."""
from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()
TEST_PASSWORD = 'senha12345'  # nosec B105


@pytest.mark.django_db
def test_create_user_with_required_fields():
    user = User.objects.create_user(
        first_name='João',
        last_name='Silva',
        username='joaosilva',
        role='Desenvolvedor',
        email='joao@example.com',
        password=TEST_PASSWORD,
    )

    assert user.first_name == 'João'
    assert user.last_name == 'Silva'
    assert user.username == 'joaosilva'
    assert user.role == 'Desenvolvedor'
    assert user.email == 'joao@example.com'
    assert user.check_password(TEST_PASSWORD)
    assert not user.check_password('senha_errada')


@pytest.mark.django_db
def test_create_user_without_role():
    user = User.objects.create_user(
        first_name='João',
        last_name='Silva',
        username='joaosilva2',
        email='joao_sem_role@example.com',
        password=TEST_PASSWORD,
    )

    assert user.first_name == 'João'
    assert user.last_name == 'Silva'
    assert user.username == 'joaosilva2'
    assert user.role is None or user.role == ''
    assert user.email == 'joao_sem_role@example.com'
    assert user.check_password(TEST_PASSWORD)


@pytest.mark.django_db
def test_email_must_be_unique():
    User.objects.create_user(
        first_name='João',
        last_name='Silva',
        username='joaosilva3',
        role='Dev',
        email='duplicado@example.com',
        password=TEST_PASSWORD,
    )

    with pytest.raises(Exception):
        User.objects.create_user(
            first_name='Maria',
            last_name='Souza',
            username='mariasouza',
            role='Designer',
            email='duplicado@example.com',
            password='outra_senha_123',
        )


@pytest.mark.django_db
def test_password_is_hashed_not_stored_in_plain_text():
    user = User.objects.create_user(
        first_name='Maria',
        last_name='Souza',
        username='mariasouza2',
        role='Designer',
        email='maria@example.com',
        password='minha_senha_secreta',
    )
    user.refresh_from_db()

    assert user.password != 'minha_senha_secreta'  # nosec B105
    assert user.password.startswith('pbkdf2_') or user.password.startswith('argon2$')
