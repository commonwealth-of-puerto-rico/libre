from __future__ import absolute_import

import logging

import pyinotify

from .models import SourceSpreadsheet

logger = logging.getLogger(__name__)


class EventHandler(pyinotify.ProcessEvent):
    def process_IN_MODIFY(self, event):
        logger.info('MODIFY event: %s' % unicode(event.pathname))
        for source in SourceSpreadsheet.objects.filter(path=event.pathname):
            source.import_data()


def setup_file_watcher():
    wm = pyinotify.WatchManager()
    notifier = pyinotify.ThreadedNotifier(wm, default_proc_fun=EventHandler())
    for source in SourceSpreadsheet.objects.exclude(path__exact=''):
        wm.add_watch(source.path, pyinotify.IN_MODIFY, rec=True)#, auto_add=True)
    notifier.start()
