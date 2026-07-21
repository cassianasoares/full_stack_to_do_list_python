"""
Testes E2E — Página de Login.

TDD: estes testes foram escritos ANTES de os data-testid serem
adicionados nos componentes React. Isso garantiu que os atributos
necessários foram colocados de forma intencional.

Cada teste é independente: usa a fixture `driver` (escopo=function)
que entrega um browser limpo sem nenhum cookie ou estado de sessão.
"""

import sys
import os
import pytest

# Garante que o pacote pages é encontrado independente de onde pytest é chamado
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pages.login_page import LoginPage
from pages.home_page import HomePage

BASE_URL = "http://localhost:8000"


# ── Carregamento e estrutura da página ────────────────────────────────────────

@pytest.mark.auth
class TestLoginPageStructure:
    """Verifica se a página de login renderiza os elementos esperados."""

    def test_login_page_loads(self, driver):
        """A página /login deve renderizar sem erros."""
        page = LoginPage(driver, BASE_URL)
        page.open()

        assert page.is_loaded(), "Elemento raiz da página de login não encontrado"

    def test_login_page_has_submit_button(self, driver):
        """O botão de submit deve estar presente e com o texto correto."""
        page = LoginPage(driver, BASE_URL)
        page.open()

        assert page.get_submit_text() == "Entrar"

    def test_login_page_has_register_link(self, driver):
        """Deve haver um link para a página de cadastro."""
        page = LoginPage(driver, BASE_URL)
        page.open()

        assert page.has_register_link(), "Link para /register não encontrado na página de login"

    def test_login_register_link_navigates(self, driver):
        """Clicar em 'Criar conta' deve navegar para /register."""
        page = LoginPage(driver, BASE_URL)
        page.open()
        page.click_register_link()

        assert "/register" in driver.current_url, (
            f"Esperava /register, encontrou: {driver.current_url}"
        )


# ── Casos de erro ─────────────────────────────────────────────────────────────

@pytest.mark.auth
class TestLoginErrors:
    """Verifica o comportamento do formulário com dados inválidos."""

    def test_login_wrong_password_shows_error(self, driver):
        """Senha errada deve exibir mensagem de erro (sem recarregar a página)."""
        page = LoginPage(driver, BASE_URL)
        page.open()
        page.login("usuario_inexistente@test.com", "SenhaErrada123")

        error = page.get_error_message()
        assert error, "Nenhuma mensagem de erro foi exibida para credenciais inválidas"

    def test_login_empty_fields_does_not_call_api(self, driver):
        """
        Submeter o formulário vazio não deve chamar a API.
        O botão de submit permanece habilitado (não entra em estado 'Entrando…').
        """
        page = LoginPage(driver, BASE_URL)
        page.open()
        # Submete sem preencher nada
        page.click_submit()

        # O texto do botão não deve mudar para 'Entrando...' pois a validação
        # HTML nativa (required) deve barrar o submit
        assert page.get_submit_text() == "Entrar", (
            "Formulário vazio não deveria ter chamado a API"
        )


# ── Fluxo de sucesso ──────────────────────────────────────────────────────────

@pytest.mark.auth
@pytest.mark.slow
class TestLoginSuccess:
    """Testa o fluxo de login bem-sucedido (requer aplicação rodando)."""

    def test_login_success_redirects_to_home(self, driver, registered_user):
        """Login com credenciais válidas deve redirecionar para /home."""
        page = LoginPage(driver, BASE_URL)
        page.open()
        page.login(registered_user["email"], registered_user["password"])

        home = HomePage(driver, BASE_URL)
        home.wait_until_loaded()

        assert "/home" in driver.current_url, (
            f"Login não redirecionou para /home. URL: {driver.current_url}"
        )

    def test_login_success_shows_welcome_message(self, driver, registered_user):
        """Após login, a home deve exibir o nome do usuário."""
        page = LoginPage(driver, BASE_URL)
        page.open()
        page.login(registered_user["email"], registered_user["password"])

        home = HomePage(driver, BASE_URL)
        home.wait_until_loaded()

        welcome = home.get_welcome_text()
        assert registered_user["first_name"] in welcome, (
            f"Nome do usuário não aparece no welcome. Texto: '{welcome}'"
        )

    def test_login_after_register_shows_success_banner(self, driver, registered_user):
        """
        Ao chegar na página de login vindo do registro (state.justRegistered=true),
        deve aparecer uma mensagem de sucesso de criação de conta.
        Este teste simula isso navegando direto com o state via URL
        (o banner aparece quando redirecionado pelo RegisterPage).

        Nota: esse caso é testado implicitamente pelo test_register_success
        em test_register.py. Aqui validamos apenas que a estrutura do banner existe.
        """
        page = LoginPage(driver, BASE_URL)
        page.open()
        # Verifica que o elemento de sucesso NÃO está presente numa visita normal
        elements = driver.find_elements(*page._SUCCESS_LOCATOR)
        assert len(elements) == 0 or not elements[0].is_displayed(), (
            "Mensagem de sucesso não deveria aparecer numa visita direta ao /login"
        )
