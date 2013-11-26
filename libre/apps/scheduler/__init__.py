from __future__ import absolute_import

import atexit
import logging
import sys

from .classes import LocalScheduler
from .exceptions import AlreadyScheduled, UnknownJob, UnknownJobClass
from .literals import SHUTDOWN_COMMANDS

logger = logging.getLogger(__name__)


def schedule_shutdown_on_exit():
    logger.debug('Scheduler shut down on exit')
    LocalScheduler.shutdown_all()
    LocalScheduler.clear_all()


if any([command in sys.argv for command in SHUTDOWN_COMMANDS]):
    logger.debug('Schedulers shut down on SHUTDOWN_COMMAND')
    # Shutdown any scheduler already running
    LocalScheduler.shutdown_all()
    LocalScheduler.clear_all()
    # Prevent any new scheduler afterwards to start
    LocalScheduler.lockdown()

atexit.register(schedule_shutdown_on_exit)
