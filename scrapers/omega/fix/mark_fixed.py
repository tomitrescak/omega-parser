
from prisma.enums import JobStatus

from api.db import connect
from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class CustomConfig(OmegaActionConfig):
    filter: str
    scraper_id: int
    target_field: str


class MarkFixed(OmegaAction[CustomConfig]):
    uid = "jobiq.fix.mark_fixed"

    async def _execute(self, omega: OmegaItem):

        prisma = await connect()
        jobId = str(omega.item["jobId"])
        item = await prisma.processedjob.find_first(where={"jobId": jobId})
        if item is not None:
            await prisma.processedjob.update(where={
                "id": item.id
            }, data={
                "status": JobStatus.Processed,
                "message": "fixed"
            })
            print("🎉 FIXED!")
