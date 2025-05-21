from typing import List


from prisma.types import JobSkillCreateWithoutRelationsInput

from scrapers.omega.action import OmegaAction, OmegaItem
from scrapers.omega.config import OmegaActionConfig
from scrapers.omega.exception import OmegaException


class CustomConfig(OmegaActionConfig):
    frameworks: List[str]
    title_field: str
    description_field: str
    target_field: str
    min_skills: int


class ParseSkills(OmegaAction[CustomConfig]):
    uid = "jobiq.parse_skills"

    async def init(self):

        self.title_field = self.config["title_field"]
        self.description_field = self.config["description_field"]
        self.target_field = self.config["target_field"]
        self.min_skills = self.config["min_skills"]

    async def _execute(self, omega: OmegaItem):
        item = omega.item
        skill_mappings: List[JobSkillCreateWithoutRelationsInput] = []

        title = item[self.title_field] if self.title_field in item else ""
        description = item[self.description_field] if self.description_field in item else ""

        # for each framework add those skills
        errors: List[str] = []

        # for skill_framework in self.skill_frameworks:
        #     skills = extract_skills(skill_framework, title, description)
        #     # print(f"  Extracted in {time.time() - start} sec")

        #     if len(skills) < self.min_skills:
        #         errors.append(f"{skill_framework.id}: {len(skills)}")
        #     else:
        #         skill_vector = np.zeros(len(skill_framework.names))
        #         for skill in skills:
        #             skill_vector[skill_framework.index(
        #                 skill["skillId"])] = skill["value"]
        #         skill_mappings.append(
        #             {
        #                 "skillFamilyId": skill_framework.id,
        #                 "skills": compress_json(skill_vector.tolist()),
        #                 # "relatedSkills": compress_json(find_related_skills(skill_framework, skills)),
        #             }
        #         )

        #     if len(errors) == len(self.skill_frameworks):
        #         omega.context.skipped += 1
        #         raise OmegaException(
        #             "warning", f"Not enough skills for '{title}' - {', '.join(errors)}")

        # set the skill mappings
        item[self.target_field] = skill_mappings
