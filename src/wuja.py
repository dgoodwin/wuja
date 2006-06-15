#!/usr/bin/env python

import pygtk
import gtk
import gobject

from logging import getLogger
from egg import trayicon

from log import setupLogging

# Configure logging: (needs to be done before importing our modules)
confFileLocations = ["~/.wuja/logging.conf", "./logging.conf"]
setupLogging(confFileLocations)
logger = getLogger("wuja")

from notifier import Notifier

pygtk.require('2.0')

class WujaApplication:

    def __init__(self):
        logger.info("Starting application.")

        # Maintain a map of events that have alert windows open to ensure
        # we don't popup multiple windows for the same event that hasn't
        # been confirmed by the user:
        self.__openAlerts = {}

        self.menu = gtk.Menu()

        testMenuItem = gtk.MenuItem()
        testMenuItem.add(gtk.Label("Hello World!"))
        testMenuItem.connect("activate", self.__printSomething,
            "Selected: Hello World!")
        testMenuItem.show_all()
        self.menu.append(testMenuItem)

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
        self.buildNotifier()

    def __clicked(self, widget, data):
        """ Handle mouse clicks on the tray icon. (pop up the menu) """
        # 1 = left, 2 = middle, 3 = right:
        self.menu.popup(None, None, None, data.button, data.time)

    def __printSomething(self, widget, s):
        print(s)

    def buildNotifier(self):
        self.notifier = Notifier()
        # TODO: Add timeout to periodically update the feed.
        self.notifier.attach(self) # register ourselves as an observer
        gobject.timeout_add(60000, self.notifier.checkForNotifications)
        self.notifier.checkForNotifications()

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def notify(self, event):
        """
        Triggered by the notifier when a notifaction of an event needs to
        go out to the user.
        """
        self.displayNotification(None, event)

    def displayNotification(self, widget, event):
        # Check if we already have a notification window open for this event:
        if self.__openAlerts.has_key(self.__getEventKey(event)):
            logger.debug("Alert window already open for event: " + \
                event.entry.title)
            return

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
        b.connect("clicked", self.snoozeEvent, event)
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

        self.__openAlerts[self.__getEventKey(event)] = alertWindow

    def __getEventKey(self, event):
        """ Build a unique string representation of an event. """
        return str(event.entry.id) + " " + str(event.when)

    def acceptEvent(self, widget, event):
        event.accepted = True
        logger.debug("Accepted event: " + event.entry.title)
        widget.get_parent_window().destroy()
        self.__openAlerts.pop(self.__getEventKey(event))

    def snoozeEvent(self, widget, event):
        logger.debug("Snoozed event: " + event.entry.title)
        widget.get_parent_window().destroy()
        self.__openAlerts.pop(self.__getEventKey(event))

    def main(self):
        gtk.main()

if __name__ == "__main__":
    wujaApp = WujaApplication()
    wujaApp.main()

