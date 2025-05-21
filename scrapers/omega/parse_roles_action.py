from typing import List

from prisma.types import JobRolesCreateWithoutRelationsInput

from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig
from scrapers.omega.exception import OmegaException


class CustomConfig(OmegaActionConfig):
    frameworks: List[str]
    title_field: str
    description_field: str
    target_field: str


class ParseRoles(OmegaAction[CustomConfig]):
    uid = "jobiq.parse_roles"

    async def init(self):

        self.title_field = self.config["title_field"]
        self.description_field = self.config["description_field"]
        self.target_field = self.config["target_field"]

    async def _execute(self, omega: OmegaItem):
        item = omega.item
        role_mappings: List[JobRolesCreateWithoutRelationsInput] = []

        title = item[self.title_field] if self.title_field in item else ""
        description = item[self.description_field] if self.description_field in item else ""

        if "roles" not in omega.context.reports:
            omega.context.reports["roles"] = {}
        report = omega.context.reports["roles"]

        # for jf in self.job_frameworks:
        #     assigned_role = find_role(jf, title, description)
        #     if assigned_role is not None:
        #         (_, _, _, role, rolem) = assigned_role
        #         if role is not None:
        #             role_mappings.append(
        #                 {"familyId": jf.id, "roleId": role, "match": rolem})

        #             # report findings to the context
        #             if jf.id not in report:
        #                 report[jf.id] = {}
        #             if role not in report[jf.id]:
        #                 report[jf.id][role] = {
        #                     "id": role,
        #                     "count": 1,
        #                     "jobs": [title]
        #                 }
        #             else:

        #                 report[jf.id][role]["count"] += 1
        #                 report[jf.id][role]["jobs"].append(title)
        #         else:
        #             omega.context.skipped += 1
        #             raise OmegaException(
        #                 "warning", f"No role found for job '{title}'")

        item[self.target_field] = role_mappings
