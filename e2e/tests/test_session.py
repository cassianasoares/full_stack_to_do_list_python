"""
Testes E2E — Sessão de usuário e proteção de rotas.

Testa o comportamento da aplicação em relação à autenticação:
- Rotas protegidas redirecionam usuários não autenticados para /login
- Rotas de guest redirecionam usuários autenticados para /home
- O logout invalida a sessão corretamente
"""

import sys
import os
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pages.login_page import LoginPage
from pages.home_page import HomePage

BASE_URL = "http://localhost:8000"


# ── Proteção de rotas ─────────────────────────────────────────────────────────

@pytest.mark.session
class TestRouteProtection:
    """Verifica o comportamento das rotas protegidas e de guest."""

    def test_protected_route_redirects_unauthenticated_user(self, driver):
        """
        Usuário não autenticado tentando acessar /home deve ser
        redirecionado para /login (ProtectedRoute).
        """
        home = HomePage(driver, BASE_URL)
        home.open()

        # Aguarda o redirecionamento acontecer
        WebDriverWait(driver, 10).until(EC.url_contains("/login"))

        assert "/login" in driver.current_url, (
            f"Esperava redirecionar para /login. URL: {driver.current_url}"
        )

    def test_root_redirects_unauthenticated_to_login(self, driver):
        """
        Acessar a raiz '/' sem autenticação deve redirecionar para /login
        (via /home → ProtectedRoute → /login).
        """
        driver.get(BASE_URL + "/")
        WebDriverWait(driver, 10).until(EC.url_contains("/login"))

        assert "/login" in driver.current_url, (
            f"Raiz '/' não redirecionou para /login. URL: {driver.current_url}"
        )

    def test_unknown_route_redirects_to_login(self, driver):
        """
        Rotas inexistentes devem ser capturadas pelo catch-all e redirecionar
        para /login quando o usuário não está autenticado.
        """
        driver.get(BASE_URL + "/rota-que-nao-existe")
        WebDriverWait(driver, 10).until(EC.url_contains("/login"))

        assert "/login" in driver.current_url, (
            f"Rota desconhecida não redirecionou para /login. URL: {driver.current_url}"
        )

    @pytest.mark.slow
    def test_guest_route_redirects_authenticated_user_to_home(self, authenticated_driver):
        """
        Usuário já autenticado tentando acessar /login deve ser redirecionado
        para /home (GuestRoute).
        """
        driver = authenticated_driver
        # Tenta navegar para o /login estando autenticado
        driver.get(BASE_URL + "/login")

        WebDriverWait(driver, 10).until(EC.url_contains("/home"))

        assert "/home" in driver.current_url, (
            f"GuestRoute não redirecionou usuário autenticado para /home. URL: {driver.current_url}"
        )

    @pytest.mark.slow
    def test_guest_register_route_redirects_authenticated_user(self, authenticated_driver):
        """
        Usuário autenticado tentando acessar /register deve ser redirecionado
        para /home (GuestRoute).
        """
        driver = authenticated_driver
        driver.get(BASE_URL + "/register")

        WebDriverWait(driver, 10).until(EC.url_contains("/home"))

        assert "/home" in driver.current_url, (
            f"GuestRoute em /register não redirecionou para /home. URL: {driver.current_url}"
        )


# ── Logout ────────────────────────────────────────────────────────────────────

@pytest.mark.session
@pytest.mark.slow
class TestLogout:
    """Testa o fluxo de logout."""

    def test_logout_redirects_to_login(self, authenticated_driver):
        """
        Clicar em 'Sair' deve encerrar a sessão e redirecionar para /login.
        """
        driver = authenticated_driver
        home = HomePage(driver, BASE_URL)
        home.wait_until_loaded()

        assert home.has_logout_button(), "Botão de logout não encontrado na home"
        home.click_logout()

        WebDriverWait(driver, 10).until(EC.url_contains("/login"))

        assert "/login" in driver.current_url, (
            f"Logout não redirecionou para /login. URL: {driver.current_url}"
        )

    def test_logout_invalidates_session(self, authenticated_driver):
        """
        Após logout, tentar acessar /home diretamente deve redirecionar
        de volta para /login (cookies JWT limpos).
        """
        driver = authenticated_driver
        home = HomePage(driver, BASE_URL)
        home.wait_until_loaded()
        home.click_logout()

        # Aguarda o redirecionamento do logout
        WebDriverWait(driver, 10).until(EC.url_contains("/login"))

        # Tenta acessar /home novamente após logout
        home.open()
        WebDriverWait(driver, 10).until(EC.url_contains("/login"))

        assert "/login" in driver.current_url, (
            "Após logout, /home deveria redirecionar para /login (sessão inválida)"
        )

    def test_home_displays_correct_user_after_login(self, authenticated_driver, registered_user):
        """
        A mensagem de boas-vindas deve conter o nome do usuário logado.
        """
        driver = authenticated_driver
        home = HomePage(driver, BASE_URL)
        home.wait_until_loaded()

        welcome = home.get_welcome_text()
        assert registered_user["first_name"] in welcome, (
            f"Nome '{registered_user['first_name']}' não encontrado no welcome: '{welcome}'"
        )
