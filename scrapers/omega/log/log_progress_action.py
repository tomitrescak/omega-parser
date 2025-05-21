from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class CustomConfig(OmegaActionConfig):
    message: str
    increase_current: int


class LogProgressAction(OmegaAction[CustomConfig]):
    uid = "jobiq.log_progress"

    async def init(self):
        pass

    async def _execute(self, omega: OmegaItem):
        if "increase_current" in self.config:
            omega.context.current_record += self.config["increase_current"]

        omega.context.log_progress(omega.parse_string(self.config["message"]))
