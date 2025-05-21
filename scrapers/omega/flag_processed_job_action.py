import json
from typing import Any

from api.db import connect
from scrapers.helpers import current_date
from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.exception import OmegaException

class FlagProcessedJob(OmegaAction[Any]):
    uid = "jobiq.check_processed_job"

    async def init(self):
        self.prisma = await connect()
        self.selector = self.config["selector"] if "selector" in self.config else None
        self.source_field = self.config["source_field"] if "source_field" in self.config else None

    async def _execute(self, omega: OmegaItem):

        if self.selector is not None:
            id = omega.resolve(self.selector)
        else:
            id = omega.item["jobId"]

        existing = await self.prisma.processedjob.find_first(where={
            "jobId": str(id)
        })

        if (existing is not None):
            omega.context.existing += 1
            omega.item["processedJobId"] = existing.id
            raise OmegaException(
                "info", f"Job {id} has already been processed")

        # bj = await self.prisma.job.find_first(where={
        #     "jobId": id
        # })
        # if (bj is not None):
        #     raise OmegaException(
        #         "info", f"Job {id} has already been processed")

        if existing is None:
            existing = await self.prisma.processedjob.create(data={
                "data": json.dumps(
                    omega.resolve(
                        self.source_field) if self.source_field is not None else omega.item
                ),
                "date": current_date(),
                "scraper": omega.context.scraper.id,
                "jobId": str(id)
            })

        omega.item["processedJobId"] = existing.id
