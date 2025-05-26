from bs4 import BeautifulSoup

from scrapers.helpers import Souped
from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class CustomConfig(OmegaActionConfig):
    url: str
    wait_css: str
    wait_xpath: str


class SeleniumRequest(OmegaAction[CustomConfig]):
    uid = "jobiq.request.selenium.soup"

    async def init(self):
        self.wait_css = self.config["wait_css"] if "wait_css" in self.config else None
        self.wait_xpath = self.config["wait_xpath"] if "wait_xpath" in self.config else None

    async def _execute(self, omega: OmegaItem):
        # process url
        url = omega.parse_string(self.config["url"])

        data = omega.app.selenium.load_page(url, self.wait_css, self.wait_xpath)

        omega.url = url
        omega.current_url = omega.app.selenium.driver.current_url
        
        omega.source = data
        omega.soup = Souped(BeautifulSoup(data, "html.parser"))

