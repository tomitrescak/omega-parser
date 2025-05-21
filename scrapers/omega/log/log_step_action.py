from typing_extensions import NotRequired

from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class CustomConfig(OmegaActionConfig):
    step_name: str
    step_number: int
    step_count: NotRequired[int]


class LogStepAction(OmegaAction[CustomConfig]):
    uid = "jobiq.log_step"

    async def init(self):
        pass

    async def _execute(self, omega: OmegaItem):
        omega.context.step_name = self.config["step_name"]
        omega.context.step = self.config["step_number"]

        if "step_count" in self.config:
            omega.context.steps = self.config["step_count"]
