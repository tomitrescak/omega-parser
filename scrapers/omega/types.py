from typing import Any, Dict, List, TypedDict
from typing_extensions import NotRequired

from scrapers.omega.config import OmegaConfig

class QueueProcessItemBase(TypedDict):
    slot: NotRequired[int]

class QueueProcessItem(QueueProcessItemBase):

    item: Dict[str, Any]
    scraper_id: int
    run_id: int
    config: OmegaConfig

class QueueProcessResultItemBase(TypedDict):
    slot: int
    message: str
    exception: NotRequired[str]

class QueueProcessResultItem(QueueProcessResultItemBase):
    run_id: int
    succeeded: int
    failed: int
    existing: int
    skipped: int
    errors: List[str]
    warnings: List[str]
    info: List[str]
    reports: Dict[str, Any]
    log: str
