from bs4 import BeautifulSoup

from scrapers.helpers import Souped, fetch_url
from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class CustomConfig(OmegaActionConfig):
    url: str
    query: str
    variables: str


class RequestSoup(OmegaAction[CustomConfig]):
    uid = "jobiq.request.soup"

    async def init(self):
        self.url = self.config["url"]

    async def _execute(self, omega: OmegaItem):
        # process url
        url = omega.parse_string(self.url)

        data = fetch_url(url)

        omega.url = url
        omega.source = data
        omega.soup = Souped(BeautifulSoup(data, "html.parser"))
