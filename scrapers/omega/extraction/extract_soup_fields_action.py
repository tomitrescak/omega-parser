from typing import List

from scrapers.helpers import ExtractorConfig
from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class FieldConfig(ExtractorConfig):
    selector: str
    target_field: str


class CustomConfig(OmegaActionConfig):
    fields: List[FieldConfig]


class ExtractSoupFieldsAction(OmegaAction[CustomConfig]):
    uid = "jobiq.extract.soup_fields"

    async def init(self):
        self.fields = self.config["fields"] if "fields" in self.config else []

    async def _execute(self, omega: OmegaItem):

        for field in self.fields:
            soup = omega.soup.select_one(field["selector"])
            extracted = soup.extract_field(field, omega.item)
            omega.item[field["target_field"]] = extracted
