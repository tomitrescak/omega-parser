from __future__ import annotations

import json
import random
import re
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Generic, List, Type, TypeVar

from prisma.enums import JobStatus

# import scrapers.queue
from api.db import connect
from scrapers.helpers import Souped, find_parent
from scrapers.info import ScraperInfo
from scrapers.omega.config import OmegaActionConfig, get_id_from_name
from scrapers.omega.exception import OmegaAbort, OmegaException
from libs.selenium import Selenium
from libs.progress import ProgressBar

# import scrapers.queue


pattern = r"\$\{(.*?)\}"


def myconverter(o: Any):

    if isinstance(o, datetime):
        return o.__str__()


class OmegaContext:
    def __init__(self, queue: Any, scraper: ScraperInfo, run_id: int | None):
        self.queue = queue
        self.scraper = scraper
        self.succeeded = 0
        self.failed = 0
        self.existing = 0
        self.skipped = 0
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        self.reports: Dict[str, Any] = {}
        self.running = True
        self.log = ""

        self.runId = run_id
        self.steps = 0
        self.step = 0
        self.total_records = 0
        self.current_record = 0

        self.start_time = time.time()
        self.step_start_time = time.time()

    def create_mail(self, mail: str) -> str:
        return f"""
        <h1>Hello Master 🙇🏼‍</h1> 
        <br />
        I have finished processing scraper: <i>{self.scraper.name}</i><br />
        <br />
        {self.info_text}
        <br />
        {mail}
        <br />
        <br />
        🧠 JobIQ Manager
        """
        return

    def log_progress(self, message: str, increase: int = 0, progress: ProgressBar | None = None):
        if increase > 0:
            self.current_record += increase

        if message != "":
            self.log += message + "\n"

        if progress is not None:
            progress.step(message)
            
        data = {
            "scraper": self.scraper.name,
            "scraperId": self.scraper.id,
            "runId": self.runId,
            "message": message,
            "type": self.scraper.type,
            "current": self.current_record,
            "total": self.total_records,
            "elapsed": self.step_elapsed_time,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "skipped": self.skipped,
            "estimated": self.estimated_time,
            "average": self.average_time
        }

        if (self.steps > 0):
            data["step"] = self.step
            data["stepName"] = self.step_name
            data["steps"] = self.steps
            data["totalElapsed"] = self.total_elapsed_time

        self.queue.progress(data)

        print(message)

    def start_step(self, name: str):
        self.current_record = 0
        self.step += 1
        self.step_name = name
        self.step_start_time = time.time()
        self.log += name

    @property
    def average_time(self):
        return round((time.time() - self.step_start_time) / (self.current_record or 1), 3)

    @property
    def step_elapsed_time(self):
        return time.time() - self.step_start_time

    @property
    def estimated_time(self):
        return '{:0>8}'.format(str(timedelta(seconds=int(self.average_time * (self.total_records - self.current_record)))))

    @property
    def total_elapsed_time(self):
        return time.time() - self.start_time

    @property
    def info_text(self):
        result = f"""
        Finished: <i>{datetime.now()}</i><br />
        Time: <i>{self.total_elapsed_time} sec</i><br />
        <br />
        <b>🎉 New:</b> {self.succeeded}<br />
        <b>❌ Failed:</b> {self.failed}<br />
        <b>♻️ Existing:</b> {self.existing}<br />
        <b>🤨 Skipped:</b> {self.skipped}<br />
        """
        if len(self.errors) > 0:
            result += f"""
            <h3>❌ {len(self.errors)} Errors</h3>
            {str.join("<br />", self.errors)}
            """
        if len(self.warnings) > 0:
            result += f"""
            <h3>⚠️ {len(self.warnings)} Warnings</h3>
            {str.join("<br />", self.warnings)}
            """
        # if len(self.info) > 0:
        #     result += f"""
        #     <h2>ℹ️ {len(self.info)} Info</h2>
        #     {str.join("<br />", self.info)}
        #     """
        return result


class AppContext:
    def __init__(self):
        self._selenium: Selenium | None = None

    @property
    def selenium(self):
        if self._selenium is None:
            retry = 0
            self._selenium = Selenium()

            while not self._selenium.initialised:
                try:
                    self._selenium.init()
                    print(f"🎉 Selenium Initialised!")
                except Exception as e:
                    print(f"Try #{retry} 🤨 Could not initialise selenium: {e}")
                    retry += 1
                    if (retry > 10):
                        raise OmegaException(
                            "fatal", "Could not initialise selenium")
                    time.sleep(1 + 2 * random.random())

        return self._selenium

    def cleanup(self):
        if self._selenium is not None:
            print("💀 Kill Selenium")
            self._selenium.quit()


class OmegaItem:
    def __init__(self, context: OmegaContext, app: AppContext, item: Dict[str, Any] = {}) -> None:
        self.context = context
        self.source: str = ""
        self.item = item
        self.soup: Souped = None  # type:ignore
        self.url: str = ""
        self.app: AppContext = app

    def clone(self):
        clone = OmegaItem(self.context, self.app)

        clone.source = self.source
        clone.item = self.item.copy()
        clone.soup = self.soup
        clone.url = self.url

        return clone

    def __string_replacement(self, match: re.Match[str]):
        return str(find_parent(match.group(1), self.item))

    def parse_string(self, string: str):
        result = re.sub(pattern, self.__string_replacement, string)
        return result

    def resolve(self, path: str):
        return find_parent(path, self.item)


T = TypeVar("T", bound=OmegaActionConfig)
U = TypeVar("U", bound=OmegaActionConfig)


class OmegaAction(ABC, Generic[T]):

    def __init__(self, config: T, shared_config: Any, repository: ActionRepository):
        self.config = config
        self.shared_config = shared_config
        self.repository = repository
        self.children: List[OmegaAction[Any]] | None = None

    def get_int_config(self, name: str, omega: OmegaItem, default: int = 0) -> int:
        result: int = default
        if name in omega.item:
            result = int(omega.item[name])
        elif name in self.config:
            result = self.config[name]
        elif name in self.shared_config:
            result = self.shared_config[name]
        return result
    
    def get_bool_config(self, name: str, omega: OmegaItem, default: bool = False) -> bool:
        result: bool = default
        if name in omega.item:
            result = bool(omega.item[name])
        elif name in self.config:
            result = self.config[name]
        elif name in self.shared_config:
            result = self.shared_config[name]
        return result

    def get_string_config(self, name: str, omega: OmegaItem, default: str = '') -> str:
        result = default
        if name in omega.item:
            result = omega.item[name]
        elif name in self.config:
            result = self.config[name]
        elif name in self.shared_config:
            result = self.shared_config[name]
        return result

    async def init(self):
        pass

    @abstractmethod
    async def _execute(self, omega: OmegaItem):
        pass

    async def init_children(self):
        self.config = self.config

        if "CHILDREN" in self.config:
            # create children
            self.children = []

            for child_config in self.config["CHILDREN"]:  # type: ignore
                uid = get_id_from_name(child_config["name"])

                if uid not in self.repository:
                    print(
                        f"☠️  FATAL Ω: Action {uid} not found in the repository")
                    raise OmegaException(
                        "fatal",
                        f"Action {uid} not found in the repository")

                child = self.repository[uid](
                    child_config, self.shared_config, self.repository)
                self.children.append(child)

            # init children with their default properties
            for child in self.children:
                await child.init()

    async def update_processed_job(self, omega: OmegaItem, status: JobStatus, message: str):

        if len(message) > 187:
            message = message[0:187] + "..."

        prisma = await connect()

        if "processedJobId" in omega.item:
            existing = await prisma.processedjob.find_first(where={
                "id": omega.item["processedJobId"]
            })
        elif "jobId" in omega.item:
            existing = await prisma.processedjob.find_first(where={
                "jobId": str(omega.item["jobId"])
            })
        else:
            existing = None

        if existing is not None:
            data = json.loads(existing.data)
            if self.shared_config["processed"]["target"] not in data:
                data[self.shared_config["processed"]["target"]] = {}

            for key in omega.item:
                if "processed" in self.shared_config:
                    if key in self.shared_config["processed"]["ignore"]:
                        continue
                    data[self.shared_config["processed"]
                         ["target"]][key] = omega.item[key]

            await prisma.processedjob.update(
                where={"id": existing.id},
                data={
                    "status": status,
                    "message": message,
                    "data": json.dumps(data, default=myconverter)
                }
            )

    def raise_exception(self, e: Exception):
        # type: ignore
        if not 'boundary' in self.config or self.config['boundary'] == False:
            raise e
        else:
            print(f"🛡️  {e}")

    async def __execute_process(self, process: Callable[[OmegaItem], Any], omega: OmegaItem):
        # check if we are stopped
        if not omega.context.running:
            raise OmegaAbort()
        try:
            await process(omega)
        except OmegaException as e:
            if e.severity == "fatal":
                print("☠️ FATAL Ω " + e.message + f" at ({omega.url})")
                self.raise_exception(e)
            else:
                message = e.message + f" at ({omega.url})"

                if e.severity == "error":
                    omega.context.errors.append(message)
                    omega.context.failed += 1

                    await self.update_processed_job(omega, JobStatus.Error, message)

                    self.raise_exception(OmegaException('abort', message))
                elif e.severity == "warning":
                    omega.context.warnings.append(message)

                    await self.update_processed_job(omega, JobStatus.Warning, message)
                elif e.severity == "info":
                    omega.context.info.append(message)
                elif e.severity == "abort":
                    self.raise_exception(e)

            print(f"Ω {e.severity}: {e.message}")
        except OmegaAbort:
            raise
        except Exception as e:
            message = f"Unexpected Error '{str(e)}' at ({omega.url})"
            omega.context.errors.append(message)
            omega.context.failed += 1

            print(f"NOT Ω {str(e)}")

            await self.update_processed_job(omega, JobStatus.Error, message)
            self.raise_exception(OmegaException('abort', message))

    async def execute(self, omega: OmegaItem):
        await self.__execute_process(self._execute, omega)

    async def __execute_children_safe(self, omega: OmegaItem):
        if self.children is not None:
            for child in self.children:
                if "if" in child.config:
                    if not eval(omega.parse_string(child.config["if"])):
                        continue
                await child._execute(omega)

    async def execute_children(self, omega: OmegaItem):
        await self.__execute_process(self.__execute_children_safe, omega)


class SharedOmegaAction(OmegaAction[T], Generic[T, U]):

    def __init__(self, config: T, shared_config: U, repository: ActionRepository):

        self.shared_config = shared_config
        super().__init__(config, shared_config, repository)


ActionRepository = Dict[str, Type[OmegaAction[Any]]]
