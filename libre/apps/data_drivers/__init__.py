from __future__ import absolute_import

from scheduler import LocalScheduler

from .schedules import check_sources_for_import
from .settings import SCHEDULER_RESOLUTION

local_scheduler = LocalScheduler('Data driver scheduler')
local_scheduler.add_interval_job(name='check_sources_for_import', label='check_sources_for_import', function=check_sources_for_import, seconds=SCHEDULER_RESOLUTION)

local_scheduler.start()
