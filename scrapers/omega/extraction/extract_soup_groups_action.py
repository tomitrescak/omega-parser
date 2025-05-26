from typing import List

from typing_extensions import NotRequired

from scrapers.helpers import ExtractorConfig
from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class FieldConfig(ExtractorConfig):
    selector: str
    target_field: str


class CustomConfig(OmegaActionConfig, ExtractorConfig):
    fields: NotRequired[List[FieldConfig]]
    selector: str
    target_field: str
    count_field: NotRequired[str]
    record_count: NotRequired[str]

    on_none: NotRequired[str]
    on_value: NotRequired[str]


class ExtractSoupGroupsAction(OmegaAction[CustomConfig]):
    uid = "jobiq.extract.soup_groups"

    async def init(self):

        self.selector = self.config["selector"]
        self.target_field = self.config["target_field"]
        self.fields = self.config["fields"] if "fields" in self.config else []

        await super().init_children()

    async def _execute(self, omega: OmegaItem):
        

        # select all parent fields
        soups = omega.soup.select(self.selector)

        # if count_field is specified, set the count
        if "count_field" in self.config:
            omega.item[self.config["count_field"]] = len(soups)

        # if record_count is specified, set the count
        if "record_count" in self.config:
            page_count = int(omega.parse_string(self.config["record_count"]))
            omega.context.total_records = page_count * len(soups)

        found = False

        # in each selected field extract what is necessary
        for parent in soups:

            # first extract the field
            if len(self.fields) == 0:
                item = parent.extract_field(self.config, omega.item)
            else:
                item = {}
                # construct the new field
                for field in self.fields:
                    soup = parent.select_one(field["selector"])
                    extracted = soup.extract_field(field, omega.item)
                    item[field["target_field"]] = extracted

            # if we have no value we may choose to skip
            if item is None and "on_none" in self.config:
                if self.config["on_none"] == "skip":
                    continue

            # now process the children with the new context
            child_item = omega.clone()
            child_item.item[self.target_field] = item

            await self.execute_children(child_item)

            found = True

            # we can stop after first item
            if "on_value" in self.config and item is not None:
                if self.config["on_value"] == "break":
                    break

        if found is False:
            raise Exception(
                f"Error fixing record ({omega.url}, {omega.item["filter"]}) - no items found for selector {self.selector}")
            

