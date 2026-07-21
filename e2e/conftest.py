"""
Fixtures compartilhadas para os testes E2E com Selenium.

Estratégias de design:
- Um único WebDriver Chrome headless é criado por sessão de teste (scope="session")
  para evitar o overhead de abrir/fechar o browser a cada teste.
- A fixture `driver` com scope="function" garante que cada teste começa limpo
  (cookies apagados, sem estado residual de sessão anterior).
- A fixture `authenticated_driver` faz login via UI uma única vez e reutiliza
  o estado para testes que precisam de autenticação.
"""

import uuid
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

BASE_URL = "http://localhost:8000"

# Credenciais de um usuário de teste criado antes da suite rodar.
# Em pipelines CI, esse usuário é criado via fixture de setup ou seed.
TEST_USER = {
    "first_name": "Teste",
    "last_name": "Selenium",
    "username": f"selenium_{uuid.uuid4().hex[:8]}",
    "email": f"selenium_{uuid.uuid4().hex[:8]}@test.com",
    "password": "Selenium@123",
}


def _chrome_options() -> Options:
    """Retorna opções do Chrome para execução headless (sem interface gráfica)."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--disable-gpu")
    return options


@pytest.fixture(scope="session")
def chrome_driver_binary():
    """Instala/localiza o ChromeDriver uma única vez por sessão."""
    return ChromeDriverManager().install()


@pytest.fixture()
def driver(chrome_driver_binary):
    """
    Fixture de WebDriver com escopo por função.
    Cada teste recebe um browser limpo (sem cookies nem sessão).
    """
    service = Service(chrome_driver_binary)
    drv = webdriver.Chrome(service=service, options=_chrome_options())
    drv.implicitly_wait(5)  # segundos de espera implícita por elementos
    yield drv
    drv.quit()


@pytest.fixture(scope="session")
def registered_user(chrome_driver_binary):
    """
    Registra um usuário de teste via UI uma única vez por sessão.
    Retorna as credenciais do usuário criado.
    """
    from pages.register_page import RegisterPage

    service = Service(chrome_driver_binary)
    drv = webdriver.Chrome(service=service, options=_chrome_options())
    drv.implicitly_wait(5)

    try:
        page = RegisterPage(drv, BASE_URL)
        page.open()
        page.fill_form(TEST_USER)
        page.submit()
        # Aguarda redirecionamento para login (confirma que o registro funcionou)
        WebDriverWait(drv, 15).until(EC.url_contains("/login"))
        assert "/login" in drv.current_url, (
            f"Registro não redirecionou para /login. URL atual: {drv.current_url}"
        )
    finally:
        drv.quit()

    return TEST_USER


@pytest.fixture()
def authenticated_driver(chrome_driver_binary, registered_user):
    """
    Fixture que entrega um WebDriver já autenticado.
    Cria uma nova sessão de browser e faz login via UI.
    """
    from pages.login_page import LoginPage
    from pages.home_page import HomePage

    service = Service(chrome_driver_binary)
    drv = webdriver.Chrome(service=service, options=_chrome_options())
    drv.implicitly_wait(5)

    page = LoginPage(drv, BASE_URL)
    page.open()
    page.login(registered_user["email"], registered_user["password"])

    # Aguarda o login ser processado e redirecionar para a home page
    home = HomePage(drv, BASE_URL)
    home.wait_until_loaded()

    yield drv
    drv.quit()


def pytest_configure(config):
    """Registra marcadores customizados para evitar warnings do pytest."""
    config.addinivalue_line("markers", "slow: testes que dependem de I/O externo")
    config.addinivalue_line("markers", "auth: testes de autenticação")
    config.addinivalue_line("markers", "session: testes de sessão e proteção de rotas")
