#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import gobject
from egg import trayicon

from notifier import Notifier

class WujaApplication:

    def __clicked(self, widget, data):
        """ Handle mouse clicks on the tray icon. (pop up the menu) """
        # 1 = left, 2 = middle, 3 = right:
        self.menu.popup(None, None, None, data.button, data.time)

    def __printSomething(self, widget, s):
        print(s)

    def hello(self, widget, data, s):
        print("Hello world! " + s)
        print(dir(data))
        print(data.button)

    def delete_event(self, widget, event, data=None):
        print "called: delete_event"
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
#        self.trayIcon.add(icon)
        self.trayIcon.connect('button_press_event', self.__clicked)

        eb = gtk.EventBox()
        eb.add(gtk.Label("Wuja"))
        self.trayIcon.add(eb)
        self.trayIcon.show_all()

        self.notifier = Notifier()
        # TODO: Add timeout to periodically update the feed.
        self.notifier.attach(self) # register ourselves as an observer
        gobject.timeout_add(5000, self.notifier.checkForNotifications)

    def notify(self):
        """
        Triggered by the notifier when a notifaction of an event needs to
        go out to the user.
        """
        print("### Notify Called ###")

    def main(self):
        gtk.main()

if __name__ == "__main__":
    wujaApp = WujaApplication()
    wujaApp.main()

