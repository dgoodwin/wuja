#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
from egg import trayicon

class WujaApplication:

    def __clicked(self, widget, data):
        """ Handle mouse clicks on the tray icon. (pop up the menu) """
        print("Clicked button: " + str(data.button))
        # TODO: Popup menu!

    def __printSomething(self, widget, data, s):
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
        icon = gtk.image_new_from_stock(gtk.STOCK_DIALOG_INFO,
            gtk.ICON_SIZE_BUTTON)

        # Build the menu to display when clicking the system tray icon:
        self.menu = gtk.Menu()
        self.menuItem = gtk.MenuItem()
        self.menuItem.add(gtk.Label("Hello World!"))
        self.menuItem.connect("activate", self.__printSomething,
            "Selected: Hello World!")
        self.menuItem.show_all()
        self.menu.append(self.menuItem)
        self.menu.show_all()

        self.trayIcon = trayicon.TrayIcon("wuja")
#        self.trayIcon.add(icon)
#        self.trayIcon.add(gtk.Label("Wuja"))
#        self.trayIcon.connect('map-event', self.hello, "map-event")
#        self.trayIcon.connect('unmap-event', self.hello, "unmap-event")
#        self.trayIcon.connect('scroll-event', self.hello, "scroll-event")
#        self.trayIcon.connect('destroy', self.hello, "destroy")

        self.trayIcon.connect('button_press_event', self.__clicked)

        eb = gtk.EventBox()
        eb.add(gtk.Label("Wuja"))
        self.trayIcon.add(eb)

        self.trayIcon.show_all()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    wujaApp = WujaApplication()
    wujaApp.main()

