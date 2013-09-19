import logging
from multiprocessing import Process

from django.conf import settings

logger = logging.getLogger(__name__)


class Job(Process):
    def submit(self, *args, **kwargs):
        if settings.JOB_PROCESSING_MODE_IMMEDIATE:
            logger.debug('Running job in immediate mode')
            return super(self.__class__, self).run(*args, **kwargs)
        else:
            logger.debug('Running job in background mode')
            return super(self.__class__, self).start(*args, **kwargs)
