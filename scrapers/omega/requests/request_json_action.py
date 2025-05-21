import time

from typing_extensions import NotRequired

from scrapers.helpers import fetch_json
from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class CustomConfig(OmegaActionConfig):
    url: str
    target_field: str
    url_field: NotRequired[str]


class RequestJsonAction(OmegaAction[CustomConfig]):
    uid = "jobiq.request.json"

    async def init(self):
        self.url = self.config["url"]

    async def _execute(self, omega: OmegaItem):
        # process url
        url = omega.parse_string(self.url)

        data = fetch_json(url)

        omega.url = url
        omega.source = data
        omega.item[self.config["target_field"]] = data

        if "url_field" in self.config:
            omega.item[self.config["url_field"]] = url

        time.sleep(1)
