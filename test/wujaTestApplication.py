""" Clone of the production Wuja application for testing purposes. """

__revision__ = "$Revision$"

import pygtk
import gtk
import gobject

from datetime import datetime, timedelta

import settestpath

from wuja.application import WujaApplication
from wuja.notifier import DEFAULT_THRESHOLD
from wuja.model import SingleOccurrenceEntry, Event
from notifierTests import TestNotifier

pygtk.require('2.0')

class TestWujaApplication(WujaApplication):
    """ Overload necessary functionality from the WujaApplication to
    prevent any communication with Google's servers, and fake an event
    in the near future.
    """

    def __init__(self):
        WujaApplication.__init__(self)

        fake_notification = gtk.MenuItem()
        fake_notification.add(gtk.Label("Fake Notification"))
        now = datetime.now()
        when = now + timedelta(seconds=15)
        fake_entry = SingleOccurrenceEntry(-1, "Fake Event", "",
            now, when, 3600, "")
        fake_event = Event(fake_entry.when, fake_entry)
        fake_notification.connect("activate", self.display_notification,
            fake_event)
        self.menu.append(fake_notification)
        self.menu.show_all()

    def build_notifier(self):
        """ Overload the parent build_notifier method to create a
        TestNotifier.
        """
        future_time = datetime.now() + timedelta(minutes=5)
        self.entry = SingleOccurrenceEntry("fakeId", "Fake Title", "",
            datetime.now(), future_time, 3600, "Gumdrop Alley")
        self.notifier = TestNotifier([self.entry])
        self.notifier.attach(self)
        gobject.timeout_add(5000, self.notifier.check_for_notifications)
        self.notifier.check_for_notifications()

if __name__ == "__main__":
    wuja_app = TestWujaApplication()
    wuja_app.main()

