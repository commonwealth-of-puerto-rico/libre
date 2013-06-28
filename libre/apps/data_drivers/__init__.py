from __future__ import absolute_import

import pyinotify

from .models import SourceSpreadsheet


class MyEventHandler(pyinotify.ProcessEvent):
    def process_IN_MODIFY(self, event):
        print "MODIFY event:", event.pathname
        for source in SourceSpreadsheet.objects.filter(path=event.pathname):
            source.import_data()


wm = pyinotify.WatchManager()
notifier = pyinotify.ThreadedNotifier(wm, default_proc_fun=MyEventHandler())
for source in SourceSpreadsheet.objects.exclude(path__exact=''):
    wm.add_watch(source.path, pyinotify.IN_MODIFY, rec=True)#, auto_add=True)
notifier.start()
