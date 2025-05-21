from __future__ import annotations

from typing import Any, List

from typing_extensions import NotRequired

from scrapers.helpers import ExtractorConfig, extract_text, find_parent
from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class FieldConfig(ExtractorConfig):
    selector: NotRequired[str]
    target_field: str
    join: NotRequired[List[FieldConfig]]
    value: NotRequired[Any]
    separator: NotRequired[str]


class CustomConfig(OmegaActionConfig):
    root: str
    fields: List[FieldConfig]


class ExtractJsonFieldsAction(OmegaAction[CustomConfig]):
    uid = "jobiq.extract.json_fields"

    async def init(self):
        self.fields = self.config["fields"] if "fields" in self.config else []

    async def combine_fields(self, root: Any, omega: OmegaItem, separator: str, fields: List[FieldConfig]):
        combined: List[str] = []
        for field in fields:

            if "target_field" in field:
                raise Exception(
                    "When combining fields we do not expect a target field")

            if "selector" in field:
                item = find_parent(field["selector"], root)
                extracted = extract_text(item, field, omega.item)

                if extracted is None:
                    continue

                # we only append if the field is not a join field
                if "join" not in field:
                    combined.append(extracted)

            if "join" in field:
                result = await self.combine_fields(root, omega, separator, field["join"])
                combined.append(result)

            if "value" in field:
                combined.append(field["value"])

        return str.join(separator, combined)

    async def _execute(self, omega: OmegaItem):
        root = find_parent(
            self.config["root"], omega.item) if "root" in self.config else omega.item

        for field in self.fields:
            if "selector" in field:
                item = find_parent(field["selector"], root)
                extracted = extract_text(item, field, omega.item)
                omega.item[field["target_field"]] = extracted
            elif "join" in field:
                separator = self.config["separator"] if "separator" in self.config else "\n"
                combined = await self.combine_fields(root, omega, separator, field["join"])
                extracted = extract_text(combined, field, omega.item)
                omega.item[field["target_field"]] = extracted
            elif "value" in field:
                omega.item[field["target_field"]] = field["value"]
            else:
                raise Exception("Invalid field configuration")
