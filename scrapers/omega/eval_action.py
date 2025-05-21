from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class CustomConfig(OmegaActionConfig):
    expression: str
    target_field: str


class EvalAction(OmegaAction[CustomConfig]):
    uid = "jobiq.eval"

    async def _execute(self, omega: OmegaItem):
        omega.item[self.config["target_field"]] = eval(
            omega.parse_string(self.config["expression"])
        )
