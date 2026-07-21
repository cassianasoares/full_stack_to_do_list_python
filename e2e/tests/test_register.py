"""
Testes E2E — Página de Registro.

Os testes de validação client-side (senhas divergentes, senha curta)
NÃO fazem chamadas de rede — são executados pelo JavaScript do React
antes do submit. Por isso são rápidos e determinísticos.
"""

import sys
import os
import uuid
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pages.register_page import RegisterPage
from pages.login_page import LoginPage

BASE_URL = "http://localhost:8000"


def _unique_user() -> dict:
    """Gera dados únicos para evitar conflito de e-mail/username entre testes."""
    uid = uuid.uuid4().hex[:8]
    return {
        "first_name": "Usuário",
        "last_name": "Teste",
        "username": f"user_{uid}",
        "email": f"user_{uid}@test.com",
        "password": "Senha@12345",
        "password_match": "Senha@12345",
    }


# ── Estrutura da página ───────────────────────────────────────────────────────

@pytest.mark.auth
class TestRegisterPageStructure:
    """Verifica se a página de registro renderiza corretamente."""

    def test_register_page_loads(self, driver):
        """A página /register deve renderizar sem erros."""
        page = RegisterPage(driver, BASE_URL)
        page.open()

        assert page.is_loaded(), "Elemento raiz da página de registro não encontrado"

    def test_register_page_has_login_link(self, driver):
        """Deve haver um link para a página de login."""
        page = RegisterPage(driver, BASE_URL)
        page.open()

        assert page.has_login_link(), "Link para /login não encontrado na página de registro"

    def test_register_login_link_navigates(self, driver):
        """Clicar em 'Entrar' deve navegar para /login."""
        page = RegisterPage(driver, BASE_URL)
        page.open()
        page.click_login_link()

        assert "/login" in driver.current_url, (
            f"Esperava /login, encontrou: {driver.current_url}"
        )


# ── Validações client-side ────────────────────────────────────────────────────

@pytest.mark.auth
class TestRegisterClientValidation:
    """
    Testa validações executadas pelo React antes de qualquer chamada de rede.
    Esses testes são rápidos e não dependem do backend estar rodando.
    """

    def test_passwords_mismatch_shows_error(self, driver):
        """Senhas diferentes devem exibir erro sem chamar a API."""
        page = RegisterPage(driver, BASE_URL)
        page.open()

        data = _unique_user()
        data["password_match"] = "SenhaCompletamenteDiferente@99"
        page.fill_form(data)
        page.submit()

        error = page.get_error_message()
        assert "coincidem" in error.lower(), (
            f"Esperava mensagem sobre senhas diferentes, recebeu: '{error}'"
        )

    def test_short_password_shows_error(self, driver):
        """Senha com menos de 8 caracteres deve exibir erro de validação."""
        page = RegisterPage(driver, BASE_URL)
        page.open()

        data = _unique_user()
        data["password"] = "123"
        data["password_match"] = "123"
        page.fill_form(data)
        page.submit()

        error = page.get_error_message()
        assert "8" in error or "mínimo" in error.lower(), (
            f"Esperava mensagem sobre tamanho mínimo, recebeu: '{error}'"
        )

    def test_mismatched_and_short_password_prioritizes_mismatch(self, driver):
        """
        Quando as senhas são diferentes E curtas, o erro de mismatch deve
        aparecer primeiro (ordem definida pela lógica do componente RegisterPage).
        """
        page = RegisterPage(driver, BASE_URL)
        page.open()

        data = _unique_user()
        data["password"] = "123"
        data["password_match"] = "456"
        page.fill_form(data)
        page.submit()

        error = page.get_error_message()
        assert "coincidem" in error.lower(), (
            f"Esperava erro de mismatch como prioridade, recebeu: '{error}'"
        )


# ── Fluxo de sucesso ──────────────────────────────────────────────────────────

@pytest.mark.auth
@pytest.mark.slow
class TestRegisterSuccess:
    """Testa o fluxo de registro completo (requer backend rodando)."""

    def test_register_success_redirects_to_login(self, driver):
        """Registro bem-sucedido deve redirecionar para /login."""
        page = RegisterPage(driver, BASE_URL)
        page.open()
        page.fill_form(_unique_user())
        page.submit()

        # Aguarda redirecionamento
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        WebDriverWait(driver, 10).until(EC.url_contains("/login"))

        assert "/login" in driver.current_url, (
            f"Esperava redirecionar para /login após registro. URL: {driver.current_url}"
        )

    def test_register_success_shows_success_banner_on_login(self, driver):
        """
        Após registro bem-sucedido, a página de login deve exibir
        a mensagem de confirmação 'Conta criada com sucesso!'.
        """
        page = RegisterPage(driver, BASE_URL)
        page.open()
        page.fill_form(_unique_user())
        page.submit()

        login_page = LoginPage(driver, BASE_URL)
        success_msg = login_page.get_success_message()

        assert "sucesso" in success_msg.lower(), (
            f"Esperava mensagem de sucesso na tela de login, recebeu: '{success_msg}'"
        )

    def test_register_duplicate_email_shows_error(self, driver, registered_user):
        """
        Tentar registrar com um e-mail já existente deve exibir
        mensagem de erro retornada pelo backend.
        """
        page = RegisterPage(driver, BASE_URL)
        page.open()

        duplicate = _unique_user()
        duplicate["email"] = registered_user["email"]  # e-mail já cadastrado
        duplicate["username"] = f"outro_{uuid.uuid4().hex[:6]}"  # username diferente
        page.fill_form(duplicate)
        page.submit()

        error = page.get_error_message()
        assert error, "Nenhuma mensagem de erro para e-mail duplicado"
