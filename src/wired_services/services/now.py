from datetime import datetime, timezone, timedelta
from typing import Annotated

from ..servicetools import wired_service, Wired
from ..interfaces import INow, ISettings


@wired_service(INow)
class NowService:
    """Ex no-deps: Service with no deps, not very interesting. """

    local_tz_offset_hours: Annotated[int, Wired(ISettings, key='hello.local_tz_offset_hours')]

    def __init__(self, local_tz_offset_hours: int):
        self.local_tz_offset_hours = local_tz_offset_hours

    def get_local_now(self):
        return datetime.now(timezone(timedelta(hours=self.local_tz_offset_hours)))
