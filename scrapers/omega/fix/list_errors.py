import json

from prisma.enums import JobStatus
from prisma.types import ProcessedJobWhereInput

from api.db import connect
from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class CustomConfig(OmegaActionConfig):
    filter: str
    scraper_id: int
    target_field: str
    count_field: str
    take: int


class ListErrorAction(OmegaAction[CustomConfig]):
    uid = "jobiq.fix.list_errors"

    async def init(self):

        await super().init_children()

    async def _execute(self, omega: OmegaItem):

        take = self.get_int_config('take', omega, 0)
        fix_filter = self.get_string_config('filter', omega, '')
        scraper_id = self.get_int_config('scraper_id', omega, 12)

        db_filter: ProcessedJobWhereInput = {
            "status": JobStatus.Error,
            "scraper": scraper_id
        }

        prisma = await connect()

        if fix_filter != '':
            db_filter["message"] = {
                "contains": fix_filter
            }

        total = await prisma.processedjob.count(where=db_filter)
        total = take if take > 0 and take < total else total

        print(f"👾 Fixing {total} records")

        omega.context.total_records = total
        single_take = 20

        if 'count_field' in self.config:
            omega.item[self.config["count_field"]] = total

        i = 0
        skip = 0
        while total > 0:
            records = await prisma.processedjob.find_many(where=db_filter, skip=skip, take=single_take)

            if (len(records) == 0):
                print("🚀 No more records to fix")
                break

            for record in records:
                new_item = omega.clone()
                if "index_field" in self.config:
                    new_item.item[self.config["index_field"]] = i
                new_item.item[self.config["target_field"]] = {
                    **json.loads(record.data)['result'],
                    "jobId": record.jobId,
                }
                await self.execute_children(new_item)

            total -= single_take
            skip += single_take
