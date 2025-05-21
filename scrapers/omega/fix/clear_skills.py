from api.db import connect
from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class CustomConfig(OmegaActionConfig):
    filter: str
    scraper_id: int
    target_field: str


class ClearSkills(OmegaAction[CustomConfig]):
    uid = "jobiq.fix.clear_skills"

    async def _execute(self, omega: OmegaItem):

        prisma = await connect()
        jobId = omega.item["jobId"]
        item = await prisma.job.find_first(where={"jobId": jobId})
        if item is not None:
            await prisma.jobskill.delete_many(where={
                "jobId": item.id
            })
            await prisma.job.delete(where={"id": item.id})
            print("CLEARED JOB")
