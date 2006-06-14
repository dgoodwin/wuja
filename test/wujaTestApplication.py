import pygtk
import gtk
import gobject

from datetime import datetime, timedelta

import settestpath

from wuja import WujaApplication
from notifier import DEFAULT_THRESHOLD
from model import SingleOccurrenceEntry, Event
from notifierTests import TestNotifier

pygtk.require('2.0')

class TestWujaApplication(WujaApplication):
    def __init__(self):
        WujaApplication.__init__(self)

        fakeNotification = gtk.MenuItem()
        fakeNotification.add(gtk.Label("Fake Notification"))
        now = datetime.now()
        when = now + timedelta(seconds=15)
        fakeEntry = SingleOccurrenceEntry(-1, "Fake Event", "",
            now, when, 3600, "")
        fakeEvent = Event(fakeEntry.when, fakeEntry)
        fakeNotification.connect("activate", self.displayNotification,
            fakeEvent)
        self.menu.append(fakeNotification)
        self.menu.show_all()

    def buildNotifier(self):
        futureTime = datetime.now() + timedelta(minutes=5)
        self.entry = SingleOccurrenceEntry("fakeId", "Fake Title", "",
            datetime.now(), futureTime, 3600, "Gumdrop Alley")
        self.notifier = TestNotifier([self.entry])
        self.notifier.attach(self)
        gobject.timeout_add(5000, self.notifier.checkForNotifications)
        self.notifier.checkForNotifications()

if __name__ == "__main__":
    wujaApp = TestWujaApplication()
    wujaApp.main()

