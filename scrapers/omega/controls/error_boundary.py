from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class CustomConfig(OmegaActionConfig):
    log: str


class ErrorBoundaryAction(OmegaAction[CustomConfig]):
    uid = "jobiq.controls.error_boundary"

    async def init(self):
        await super().init_children()

    async def _execute(self, omega: OmegaItem):
        try:
            await self.execute_children(omega)
        except Exception as e:
            print(f"🛡️ {e}")
