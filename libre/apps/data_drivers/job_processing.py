from multiprocessing import Process


class Job(Process):
    def submit(self, *args, **kwargs):
        return super(self.__class__, self).start(*args, **kwargs)
