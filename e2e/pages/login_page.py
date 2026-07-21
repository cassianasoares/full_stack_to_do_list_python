"""
Page Object Model — Página de Login.

Encapsula todos os seletores e ações da página /login.
Os testes nunca interagem diretamente com o WebDriver; usam apenas
os métodos desta classe. Isso garante que mudanças no HTML exijam
alterações apenas aqui, não nos testes.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginPage:
    # Seletores por data-testid — robustos a mudanças de estilo
    _PAGE_LOCATOR = (By.CSS_SELECTOR, "[data-testid='login-page']")
    _EMAIL_LOCATOR = (By.CSS_SELECTOR, "[data-testid='login-email']")
    _PASSWORD_LOCATOR = (By.CSS_SELECTOR, "[data-testid='login-password']")
    _SUBMIT_LOCATOR = (By.CSS_SELECTOR, "[data-testid='login-submit']")
    _ERROR_LOCATOR = (By.CSS_SELECTOR, "[data-testid='login-error']")
    _SUCCESS_LOCATOR = (By.CSS_SELECTOR, "[data-testid='login-success']")
    _REGISTER_LINK_LOCATOR = (By.CSS_SELECTOR, "[data-testid='login-register-link']")

    def __init__(self, driver: WebDriver, base_url: str) -> None:
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, timeout=10)

    # ── Navegação ──────────────────────────────────────────────────────────────

    def open(self) -> "LoginPage":
        """Navega para a página de login e aguarda o carregamento."""
        self.driver.get(f"{self.base_url}/login")
        self.wait.until(EC.presence_of_element_located(self._PAGE_LOCATOR))
        return self

    # ── Ações ──────────────────────────────────────────────────────────────────

    def fill_email(self, email: str) -> "LoginPage":
        field = self.driver.find_element(*self._EMAIL_LOCATOR)
        field.clear()
        field.send_keys(email)
        return self

    def fill_password(self, password: str) -> "LoginPage":
        field = self.driver.find_element(*self._PASSWORD_LOCATOR)
        field.clear()
        field.send_keys(password)
        return self

    def click_submit(self) -> "LoginPage":
        self.driver.find_element(*self._SUBMIT_LOCATOR).click()
        return self

    def login(self, email: str, password: str) -> "LoginPage":
        """Atalho: preenche e submete o formulário."""
        self.fill_email(email)
        self.fill_password(password)
        self.click_submit()
        return self

    def click_register_link(self) -> "LoginPage":
        self.driver.find_element(*self._REGISTER_LINK_LOCATOR).click()
        return self

    # ── Assertions / Queries ───────────────────────────────────────────────────

    def is_loaded(self) -> bool:
        """Retorna True se a página de login está visível."""
        try:
            return self.driver.find_element(*self._PAGE_LOCATOR).is_displayed()
        except Exception:
            return False

    def get_error_message(self) -> str:
        """Aguarda e retorna o texto da mensagem de erro."""
        el = self.wait.until(EC.visibility_of_element_located(self._ERROR_LOCATOR))
        return el.text

    def get_success_message(self) -> str:
        """Aguarda e retorna o texto da mensagem de sucesso."""
        el = self.wait.until(EC.visibility_of_element_located(self._SUCCESS_LOCATOR))
        return el.text

    def has_register_link(self) -> bool:
        try:
            return self.driver.find_element(*self._REGISTER_LINK_LOCATOR).is_displayed()
        except Exception:
            return False

    def get_submit_text(self) -> str:
        return self.driver.find_element(*self._SUBMIT_LOCATOR).text
