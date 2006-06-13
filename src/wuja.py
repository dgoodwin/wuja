#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import gobject
from egg import trayicon

from notifier import Notifier

# TODO: Remove these:
from model import SingleOccurrenceEntry, Event
import datetime

class WujaApplication:

    def __clicked(self, widget, data):
        """ Handle mouse clicks on the tray icon. (pop up the menu) """
        # 1 = left, 2 = middle, 3 = right:
        self.menu.popup(None, None, None, data.button, data.time)

    def __printSomething(self, widget, s):
        print(s)

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__(self):
        self.menu = gtk.Menu()

        testMenuItem = gtk.MenuItem()
        testMenuItem.add(gtk.Label("Hello World!"))
        testMenuItem.connect("activate", self.__printSomething,
            "Selected: Hello World!")
        testMenuItem.show_all()
        self.menu.append(testMenuItem)

        # TODO: Remove:
        fakeNotification = gtk.MenuItem()
        fakeNotification.add(gtk.Label("Fake Notification"))
        now = datetime.datetime.now()
        when = now + datetime.timedelta(seconds=15)
        fakeEntry = SingleOccurrenceEntry(-1, "Fake Event", "",
            now, when, 2600, "")
        fakeEvent = Event(fakeEntry.when, fakeEntry)
        fakeNotification.connect("activate", self.displayNotification,
            fakeEvent)
        self.menu.append(fakeNotification)

        self.menu.append(gtk.SeparatorMenuItem())

        quitMenuItem = gtk.MenuItem()
        quitMenuItem.add(gtk.Label("Quit"))
        quitMenuItem.connect("activate", self.destroy)
        quitMenuItem.show_all()
        self.menu.append(quitMenuItem)

        self.menu.show_all()

        icon = gtk.image_new_from_stock(gtk.STOCK_DIALOG_INFO,
            gtk.ICON_SIZE_BUTTON)

        self.trayIcon = trayicon.TrayIcon("wuja")
        self.trayIcon.connect('button_press_event', self.__clicked)

        eb = gtk.EventBox()
        eb.add(gtk.Label("Wuja"))
        self.trayIcon.add(eb)
        self.trayIcon.show_all()

        self.notifier = Notifier(1)
        # TODO: Add timeout to periodically update the feed.
        self.notifier.attach(self) # register ourselves as an observer
        gobject.timeout_add(5000, self.notifier.checkForNotifications)

    def notify(self, event):
        """
        Triggered by the notifier when a notifaction of an event needs to
        go out to the user.
        """
        print("Event triggered: " + event.entry.title + " " + str(event.when))
        self.displayNotification(None, event)

    def displayNotification(self, widget, event):
        box = gtk.VBox()

        l = gtk.Label("Wake Up Jackass...")
        l.show()
        box.pack_start(l)

        l = gtk.Label(event.entry.title)
        l.show()
        box.pack_start(l)

        l = gtk.Label(event.entry.description)
        l.show()
        box.pack_start(l)

        l = gtk.Label(event.when.strftime("%a %b %d %Y - %H:%M%P"))
        l.show()
        box.pack_start(l)

        buttonBox = gtk.HBox()
        b = gtk.Button("Accept")
        b.connect("clicked", self.acceptEvent, event)
        b.show()
        buttonBox.pack_start(b)

        b = gtk.Button("Snooze")
        b.connect("clicked", self.destroy)
        b.show()
        buttonBox.pack_start(b)

        buttonBox.show()
        box.pack_start(buttonBox)

        box.show()

        alertWindow = gtk.Window()
        alertWindow.set_title("Alert")
        alertWindow.add(box)
        alertWindow.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)

        alertWindow.show()

    def acceptEvent(self, widget, event):
        event.accepted = True
        print("Accepted event: " + event.entry.title)
        widget.get_parent_window().destroy()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    wujaApp = WujaApplication()
    wujaApp.main()

