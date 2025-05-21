# register actions
from typing import Any, Dict, Type

from scrapers.omega.action import OmegaAction
from scrapers.omega.controls.error_boundary import ErrorBoundaryAction
from scrapers.omega.controls.for_each_action import ForEachAction
from scrapers.omega.controls.if_action import IfAction
from scrapers.omega.controls.repeat_action import Repeat
# from scrapers.omega.config import OmegaActionConfig
from scrapers.omega.eval_action import EvalAction
from scrapers.omega.extraction.extract_json_fields_action import \
    ExtractJsonFieldsAction
from scrapers.omega.extraction.extract_soup_fields_action import \
    ExtractSoupFieldsAction
from scrapers.omega.extraction.extract_soup_groups_action import \
    ExtractSoupGroupsAction
from scrapers.omega.fix.clear_skills import ClearSkills
from scrapers.omega.fix.list_errors import ListErrorAction
from scrapers.omega.fix.mark_fixed import MarkFixed
from scrapers.omega.flag_processed_job_action import FlagProcessedJob
from scrapers.omega.graphql_query_action import GraphqlRequest
from scrapers.omega.log.log_action import LogAction
from scrapers.omega.log.log_progress_action import LogProgressAction
from scrapers.omega.log.log_step_action import LogStepAction
from scrapers.omega.multiprocessing.merge_processes_action import MergeProcess
from scrapers.omega.multiprocessing.start_process_action import StartProcess
from scrapers.omega.parse_roles_action import ParseRoles
from scrapers.omega.parse_skills_action import ParseSkills
from scrapers.omega.requests.request_json_action import RequestJsonAction
from scrapers.omega.requests.request_selenium_soup_action import \
    SeleniumRequest
from scrapers.omega.requests.request_soup_action import RequestSoup
from scrapers.omega.save_job_action import SaveJob
from scrapers.omega.selenium.click_action import SeleniumClick
from scrapers.omega.selenium.cloudflare_human import CloudflareHuman


class OmegaActionsRepository:
    def __init__(self):
        self.actions: Dict[str, Type[OmegaAction[Any]]] = {
            SaveJob.uid: SaveJob,
            FlagProcessedJob.uid: FlagProcessedJob,
            # AI Parsers
            ParseRoles.uid: ParseRoles,
            ParseSkills.uid: ParseSkills,
            # Requests
            RequestSoup.uid: RequestSoup,
            GraphqlRequest.uid: GraphqlRequest,
            SeleniumRequest.uid: SeleniumRequest,
            # Logging
            LogAction.uid: LogAction,
            LogStepAction.uid: LogStepAction,
            LogProgressAction.uid: LogProgressAction,
            # Controls
            Repeat.uid: Repeat,
            ForEachAction.uid: ForEachAction,
            EvalAction.uid: EvalAction,
            IfAction.uid: IfAction,
            ErrorBoundaryAction.uid: ErrorBoundaryAction,
            # Extraction
            ExtractSoupFieldsAction.uid: ExtractSoupFieldsAction,
            ExtractSoupGroupsAction.uid: ExtractSoupGroupsAction,
            ExtractJsonFieldsAction.uid: ExtractJsonFieldsAction,
            RequestJsonAction.uid: RequestJsonAction, 
            # selenium
            SeleniumClick.uid: SeleniumClick,
            CloudflareHuman.uid: CloudflareHuman,
            # MultiProcessing
            StartProcess.uid: StartProcess,
            MergeProcess.uid: MergeProcess,
            # fix
            ListErrorAction.uid: ListErrorAction,
            MarkFixed.uid: MarkFixed,
            ClearSkills.uid: ClearSkills
        }

    def has(self, name: str) -> bool:
        return name in self.actions

    # async def create(self, name: str, config: OmegaActionConfig) -> OmegaAction[Any]:
    #     action = self.actions[name](config,  self.actions)

    #     await action.init()

    #     return action


repository = OmegaActionsRepository()
