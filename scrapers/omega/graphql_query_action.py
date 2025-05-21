from typing import Any, Dict

from typing_extensions import NotRequired

from scrapers.helpers import fetch_graphql
from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig


class CustomConfig(OmegaActionConfig):
    url: str
    query: str
    query_name: str
    target_field: NotRequired[str]
    variables: Dict[str, Any]


class GraphqlRequest(OmegaAction[CustomConfig]):
    uid = "jobiq.request.graphql"

    async def init(self):
        self.url = self.config["url"]
        self.query = self.config["query"]
        self.variables = self.config["variables"]
        self.target_field = self.config["target_field"] if "target_field" in self.config else None

    async def _execute(self, omega: OmegaItem):
        # process url
        url = omega.parse_string(self.url)

        # parse variables and add values from the item
        parsed_variables = {}
        for key, value in self.variables.items():
            parsed_variables[key] = omega.parse_string(value)

        data = fetch_graphql(url, self.query, parsed_variables)

        omega.url = url
        omega.source = data

        if self.target_field is not None:
            omega.item[self.target_field] = next(iter(data["data"].values()))
        else:
            omega.item = {
                **omega.item,
                **data["data"][self.config["query_name"]]
            }
