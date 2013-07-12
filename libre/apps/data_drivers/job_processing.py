from multiprocessing import Process

from django.conf import settings


class Job(Process):
    def submit(self, *args, **kwargs):
        if settings.JOB_PROCESSING_MODE_IMMEDIATE:
            return super(self.__class__, self).run(*args, **kwargs)
        else:
            return super(self.__class__, self).start(*args, **kwargs)
