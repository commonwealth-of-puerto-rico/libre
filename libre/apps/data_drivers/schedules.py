from __future__ import absolute_import

import datetime
import logging

import croniter

from .models import Source
from .settings import SCHEDULER_RESOLUTION

logger = logging.getLogger(__name__)


def check_sources_for_import():
    logger.debug('check sources task')

    now = datetime.datetime.now()

    for source in Source.objects.filter(schedule_enabled=True):
        iterator = croniter.croniter(source.scheduler_string, now)
        if (iterator.get_current(datetime.datetime) - now).seconds <= SCHEDULER_RESOLUTION:
            logger.debug('triggering scheduled check_source_data for source pk: %d' % source.pk)
            source.check_source_data()
