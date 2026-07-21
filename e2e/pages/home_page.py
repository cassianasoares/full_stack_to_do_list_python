"""
Page Object Model — Página Home (área autenticada).
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class HomePage:
    _PAGE_LOCATOR = (By.CSS_SELECTOR, "[data-testid='home-page']")
    _WELCOME_LOCATOR = (By.CSS_SELECTOR, "[data-testid='home-welcome']")
    _LOGOUT_LOCATOR = (By.CSS_SELECTOR, "[data-testid='home-logout']")

    def __init__(self, driver: WebDriver, base_url: str) -> None:
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, timeout=10)

    # ── Navegação ──────────────────────────────────────────────────────────────

    def open(self) -> "HomePage":
        self.driver.get(f"{self.base_url}/home")
        return self

    def wait_until_loaded(self) -> "HomePage":
        self.wait.until(EC.presence_of_element_located(self._PAGE_LOCATOR))
        return self

    # ── Ações ──────────────────────────────────────────────────────────────────

    def click_logout(self) -> "HomePage":
        self.driver.find_element(*self._LOGOUT_LOCATOR).click()
        return self

    # ── Assertions / Queries ───────────────────────────────────────────────────

    def is_loaded(self) -> bool:
        try:
            return self.driver.find_element(*self._PAGE_LOCATOR).is_displayed()
        except Exception:
            return False

    def get_welcome_text(self) -> str:
        el = self.wait.until(EC.visibility_of_element_located(self._WELCOME_LOCATOR))
        return el.text

    def has_logout_button(self) -> bool:
        try:
            return self.driver.find_element(*self._LOGOUT_LOCATOR).is_displayed()
        except Exception:
            return False
