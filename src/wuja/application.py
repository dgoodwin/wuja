#!/usr/bin/env python

""" The main Wuja GTK application. """

__revision__ = "$Rev"

import pygtk
import gtk
import gobject
import os.path

from logging import getLogger
from egg import trayicon

from wuja.log import setupLogging

# Configure logging: (needs to be done before importing our modules)
confFileLocations = ["~/.wuja/logging.conf", "./logging.conf"]
setupLogging(confFileLocations)
logger = getLogger("wuja")

from wuja.notifier import Notifier

pygtk.require('2.0')

class WujaApplication:
    """ The main Wuja application. """

    def __init__(self):
        logger.info("Starting application.")

        # Maintain a map of events that have alert windows open to ensure
        # we don't popup multiple windows for the same event that hasn't
        # been confirmed by the user:
        self.__open_alerts = {}

        self.menu = gtk.Menu()

        test_menu_item = gtk.MenuItem()
        test_menu_item.add(gtk.Label("Hello World!"))
        test_menu_item.connect("activate", self.__print_something,
            "Selected: Hello World!")
        test_menu_item.show_all()
        self.menu.append(test_menu_item)

        self.menu.append(gtk.SeparatorMenuItem())

        quit_menu_item = gtk.MenuItem()
        quit_menu_item.add(gtk.Label("Quit"))
        quit_menu_item.connect("activate", self.destroy)
        quit_menu_item.show_all()
        self.menu.append(quit_menu_item)

        self.menu.show_all()

        #icon = gtk.image_new_from_stock(gtk.STOCK_DIALOG_INFO,
        #    gtk.ICON_SIZE_BUTTON)

        self.tray_icon = trayicon.TrayIcon("wuja")
        self.tray_icon.connect('button_press_event', self.__clicked)

        event_box = gtk.EventBox()
        event_box.add(gtk.Label("Wuja"))
        self.tray_icon.add(event_box)
        self.tray_icon.show_all()
        self.notifier = None
        self.build_notifier()

    def __clicked(self, widget, data):
        """ Handle mouse clicks on the tray icon. (pop up the menu) """
        # 1 = left, 2 = middle, 3 = right:
        self.menu.popup(None, None, None, data.button, data.time)

    def __print_something(self, widget, message):
        """ Debugging method. """
        print(message)

    def build_notifier(self):
        """ Builds the notifier object. """
        self.notifier = Notifier()
        # TODO: Add timeout to periodically update the feed.
        self.notifier.attach(self) # register ourselves as an observer
        gobject.timeout_add(60000, self.notifier.check_for_notifications)
        self.notifier.check_for_notifications()

    def delete_event(self, widget, event, data=None):
        """ GTK function. """
        return False

    def destroy(self, widget, data=None):
        """ Quit the application. """
        gtk.main_quit()

    def notify(self, event):
        """
        Triggered by the notifier when a notifaction of an event needs to
        go out to the user.
        """
        self.display_notification(None, event)

    def display_notification(self, widget, event):
        # Check if we already have a notification window open for this event:
        if self.__open_alerts.has_key(self.__get_event_key(event)):
            logger.debug("Alert window already open for event: " + \
                event.entry.title)
            return

        box = gtk.VBox()

        label = gtk.Label("Wake Up Jackass...")
        label.show()
        box.pack_start(label)

        label = gtk.Label(event.entry.title)
        label.show()
        box.pack_start(label)

        label = gtk.Label(event.entry.description)
        label.show()
        box.pack_start(label)

        label = gtk.Label(event.when.strftime("%a %b %d %Y - %H:%M%P"))
        label.show()
        box.pack_start(label)

        button_box = gtk.HBox()
        button = gtk.Button("Accept")
        button.connect("clicked", self.accept_event, event)
        button.show()
        button_box.pack_start(button)

        button = gtk.Button("Snooze")
        button.connect("clicked", self.snooze_event, event)
        button.show()
        button_box.pack_start(button)

        button_box.show()
        box.pack_start(button_box)

        box.show()

        alert_window = gtk.Window()
        alert_window.set_title("Alert")
        alert_window.add(box)
        alert_window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)

        alert_window.show()

        self.__open_alerts[self.__get_event_key(event)] = alert_window

    def __get_event_key(self, event):
        """ Build a unique string representation of an event. """
        return str(event.entry.id) + " " + str(event.when)

    def accept_event(self, widget, event):
        """ Called when the user accepts an alert. """
        event.accepted = True
        logger.debug("Accepted event: " + event.entry.title)
        widget.get_parent_window().destroy()
        self.__open_alerts.pop(self.__get_event_key(event))

    def snooze_event(self, widget, event):
        """ Called when the user presses snooze. Destroys the alert
        window and sets appropriate status for the event in question.
        """
        logger.debug("Snoozed event: " + event.entry.title)
        widget.get_parent_window().destroy()
        self.__open_alerts.pop(self.__get_event_key(event))

    def main(self):
        """ Launches the GTK main loop. """
        gtk.main()

if __name__ == "__main__":
    wujaApp = WujaApplication()
    wujaApp.main()

