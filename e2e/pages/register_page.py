"""
Page Object Model — Página de Registro.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class RegisterPage:
    _PAGE_LOCATOR = (By.CSS_SELECTOR, "[data-testid='register-page']")
    _FIRST_NAME_LOCATOR = (By.CSS_SELECTOR, "[data-testid='register-first-name']")
    _LAST_NAME_LOCATOR = (By.CSS_SELECTOR, "[data-testid='register-last-name']")
    _USERNAME_LOCATOR = (By.CSS_SELECTOR, "[data-testid='register-username']")
    _EMAIL_LOCATOR = (By.CSS_SELECTOR, "[data-testid='register-email']")
    _ROLE_LOCATOR = (By.CSS_SELECTOR, "[data-testid='register-role']")
    _PASSWORD_LOCATOR = (By.CSS_SELECTOR, "[data-testid='register-password']")
    _PASSWORD_MATCH_LOCATOR = (By.CSS_SELECTOR, "[data-testid='register-password-match']")
    _SUBMIT_LOCATOR = (By.CSS_SELECTOR, "[data-testid='register-submit']")
    _ERROR_LOCATOR = (By.CSS_SELECTOR, "[data-testid='register-error']")
    _LOGIN_LINK_LOCATOR = (By.CSS_SELECTOR, "[data-testid='register-login-link']")

    def __init__(self, driver: WebDriver, base_url: str) -> None:
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, timeout=10)

    # ── Navegação ──────────────────────────────────────────────────────────────

    def open(self) -> "RegisterPage":
        self.driver.get(f"{self.base_url}/register")
        self.wait.until(EC.presence_of_element_located(self._PAGE_LOCATOR))
        return self

    # ── Ações ──────────────────────────────────────────────────────────────────

    def _fill(self, locator, value: str) -> "RegisterPage":
        field = self.driver.find_element(*locator)
        field.clear()
        field.send_keys(value)
        return self

    def fill_form(self, data: dict) -> "RegisterPage":
        """
        Preenche o formulário a partir de um dicionário.
        Chaves aceitas: first_name, last_name, username, email, role, password, password_match.
        """
        if "first_name" in data:
            self._fill(self._FIRST_NAME_LOCATOR, data["first_name"])
        if "last_name" in data:
            self._fill(self._LAST_NAME_LOCATOR, data["last_name"])
        if "username" in data:
            self._fill(self._USERNAME_LOCATOR, data["username"])
        if "email" in data:
            self._fill(self._EMAIL_LOCATOR, data["email"])
        if "role" in data:
            self._fill(self._ROLE_LOCATOR, data["role"])
        if "password" in data:
            self._fill(self._PASSWORD_LOCATOR, data["password"])
        # Se password_match não veio, usa o mesmo valor de password
        password_match = data.get("password_match", data.get("password", ""))
        self._fill(self._PASSWORD_MATCH_LOCATOR, password_match)
        return self

    def submit(self) -> "RegisterPage":
        self.driver.find_element(*self._SUBMIT_LOCATOR).click()
        return self

    def click_login_link(self) -> "RegisterPage":
        self.driver.find_element(*self._LOGIN_LINK_LOCATOR).click()
        return self

    # ── Assertions / Queries ───────────────────────────────────────────────────

    def is_loaded(self) -> bool:
        try:
            return self.driver.find_element(*self._PAGE_LOCATOR).is_displayed()
        except Exception:
            return False

    def get_error_message(self) -> str:
        el = self.wait.until(EC.visibility_of_element_located(self._ERROR_LOCATOR))
        return el.text

    def has_login_link(self) -> bool:
        try:
            return self.driver.find_element(*self._LOGIN_LINK_LOCATOR).is_displayed()
        except Exception:
            return False
