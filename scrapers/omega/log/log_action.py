from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class CustomConfig(OmegaActionConfig):
    text: str
    field: str


class LogAction(OmegaAction[CustomConfig]):
    uid = "jobiq.log"

    async def init(self):
        pass

    async def _execute(self, omega: OmegaItem):
        # process url
        print(
            (omega.parse_string(self.config["text"]) if "text" in self.config else "") +
            (omega.resolve(self.config["field"])
             if "field" in self.config else "")
        )
