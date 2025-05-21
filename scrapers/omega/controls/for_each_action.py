from typing_extensions import NotRequired

from scrapers.helpers import find_parent
from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class CustomConfig(OmegaActionConfig):
    source_field: str
    target_field: str
    index_field: NotRequired[str]
    record_count: NotRequired[str]


class ForEachAction(OmegaAction[CustomConfig]):
    uid = "jobiq.controls.for_each"

    async def init(self):

        await super().init_children()

    async def _execute(self, omega: OmegaItem):

        values = find_parent(self.config["source_field"], omega.item)

        # if record_count is specified, set the count
        if "record_count" in self.config:
            page_count = int(omega.parse_string(self.config["record_count"]))
            omega.context.total_records = page_count * len(values)

        i = 0
        for i, value in enumerate(values):
            new_item = omega.clone()
            if "index_field" in self.config:
                new_item.item[self.config["index_field"]] = i
            new_item.item[self.config["target_field"]] = value
            await self.execute_children(new_item)
