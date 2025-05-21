from typing_extensions import NotRequired

from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class CustomConfig(OmegaActionConfig):
    condition: str
    true: str
    false: NotRequired[str]


class IfAction(OmegaAction[CustomConfig]):
    uid = "jobiq.controls.if"

    async def init(self):
        await super().init_children()

    async def _execute(self, omega: OmegaItem):
        should_execute = eval(omega.parse_string(self.config["condition"]))

        if should_execute:
            await self.execute_children(omega)
