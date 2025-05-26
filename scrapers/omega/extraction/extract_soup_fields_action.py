from typing import List

from scrapers.helpers import ExtractorConfig
from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig
from scrapers.omega.exception import OmegaException


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
            selector = field["selector"]
            
            # we can select by domains
            if "domain#" in field["selector"]:
                # find domain
                domain_name = next(
                    (d for d in self.shared_config["domains"] if d in omega.current_url), None)
                if domain_name is None:
                    raise OmegaException(
                        "error", f"Domain not found in {omega.current_url}")
                # split selector by #
                domain = self.shared_config["domains"][domain_name]
                item = field["selector"].split("#")
                # get the selector
                if item[1] not in domain:
                    raise OmegaException(
                        "error", f"Selector {item[1]} not found in {domain}")
                selector = domain[item[1]]
            
            soup = omega.soup.select_one(selector)
            extracted = soup.extract_field(field, omega.item)
            omega.item[field["target_field"]] = extracted
