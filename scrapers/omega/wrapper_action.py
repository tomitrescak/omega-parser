from typing import Any

from scrapers.omega.action import ActionRepository, OmegaAction, OmegaItem
from scrapers.omega.config import OmegaConfig


class WrapperAction(OmegaAction[Any]):
    uid = "jobiq.wrapper"

    def __init__(self, config: OmegaConfig, shared_config: Any, repository: ActionRepository):
        wrapped_config: Any = {
            "name": f"Wrapper (jobiq.wrapper)",
            "CHILDREN": config["actions"]
        }
        super().__init__(wrapped_config, shared_config, repository)

    async def init(self):
        await super().init_children()

    async def _execute(self, omega: OmegaItem):
        await self.execute_children(omega)
