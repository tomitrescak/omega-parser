from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scrapers.omega.action import OmegaItem
    # from scrapers.queue import ScraperQueue

from scrapers.omega.action import OmegaAction
from scrapers.omega.config import OmegaActionConfig

class MergeProcess(OmegaAction[OmegaActionConfig]):
    uid = "jobiq.multiprocessing.merge"

    async def _execute(self, omega: OmegaItem):
        queue = omega.context.queue
        queue.worker_manager.wait_for_slots_to_finish()
