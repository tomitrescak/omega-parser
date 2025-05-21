from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from scrapers.helpers import Souped
from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class CustomConfig(OmegaActionConfig):
    selector: str
    optional: bool
    wait_css: str


class SeleniumClick(OmegaAction[CustomConfig]):
    uid = "jobiq.selenium.click"

    async def init(self):
        self.selector = self.config["selector"]
        self.optional = self.config["optional"] if "optional" in self.config and self.config["optional"] == True else False

    async def _execute(self, omega: OmegaItem):
        try:
            element = omega.app.selenium.driver.find_element(
                By.CSS_SELECTOR, self.selector
            )
            element.click()

        except:
            if not self.optional:
                raise Exception(
                    "error", f"Element not found: {self.selector}")

        try:
            if self.config["wait_css"]:
                WebDriverWait(omega.app.selenium.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, self.config["wait_css"]))
                )

        except:
            if not self.optional:
                raise Exception(
                    "error", f"Wait element not found: {self.config['wait_css']}")

        data = omega.app.selenium.driver.page_source
        omega.source = data
        omega.soup = Souped(BeautifulSoup(data, "html.parser"))
