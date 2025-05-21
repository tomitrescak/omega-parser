from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig
from scrapers.omega.types import QueueProcessItem


class CustomConfig(OmegaActionConfig):
    max_processes: int

class StartProcess(OmegaAction[CustomConfig]):
    uid = "jobiq.multiprocessing.start"

    # async def init(self):
    #     await super().init_children()

    async def _execute(self, omega: OmegaItem):
        runId = omega.context.runId
        if runId is None:
            raise Exception("RunId is required")

        children = self.config["CHILDREN"] if "CHILDREN" in self.config else []
        if len(children) == 0:
            raise Exception("This action needs to have children")

        item: QueueProcessItem = {
            "item": omega.item,
            "slot": 0,
            "scraper_id": omega.context.scraper.id,
            "run_id": runId,
            "config": {
                "actions": children,
                "properties": self.shared_config,
            },
        }

        max_processes = self.config['max_processes'] if 'max_processes' in self.config else None

        omega.context.queue.worker_manager.schedule(item, max_processes=max_processes)
