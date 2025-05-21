from typing_extensions import NotRequired

from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class CustomConfig(OmegaActionConfig):
    count: str
    start_index: NotRequired[int]
    index_field: str


class Repeat(OmegaAction[CustomConfig]):
    uid = "jobiq.controls.repeat"

    async def init(self):

        self.count = self.config["count"]
        self.start = self.config["start_index"] if "start_index" in self.config else 0
        self.index_field = self.config["index_field"]

        await super().init_children()

    async def _execute(self, omega: OmegaItem):
        count = int(omega.parse_string(self.count))
        for i in range(self.start, count + self.start):
            new_item = omega.clone()
            new_item.item[self.index_field] = i
            await self.execute_children(new_item)
