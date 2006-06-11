#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import urllib2
import gobject
import datetime, time
from egg import trayicon

from feedparser import FeedParser

# Grab feed URL's from a config file?
feedUrl = \
"""
http://www.google.com/calendar/feeds/gqfbp7ajq1b71v5jgdtbe815ps@group.calendar.google.com/private-f404480fd9b64f2f7cb78b2a3d6daf6a/full
"""

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

        self.__updateFeed()
        gobject.timeout_add(5000, self.checkForEvents)

    def __updateFeed(self):
        # TODO: Don't read the entire calendar every time
        print("Reading entries from calendar feed:")
        xml = urllib2.urlopen(feedUrl).read()
        parser = FeedParser(xml)
        self.calendarEntries = parser.entries()
        self.events = []
        for entry in self.calendarEntries:
            print("   " + entry.title)
            startDate = datetime.datetime.now()
            endDate = startDate + datetime.timedelta(days=1)
            events = entry.events(startDate, endDate)
            for e in events:
                print("      trigger: " + str(e))
                self.events.append(e)

        # TODO: Hack for testing, remove this:
        self.events.append(datetime.datetime.now() + \
            datetime.timedelta(seconds=15))

    def checkForEvents(self):
        print("Checking for events.")
        for e in self.events:
            now = datetime.datetime.now()
            delta = now - e
            if delta > datetime.timedelta(minutes=0) and \
                delta <= datetime.timedelta(minutes=1):
                print "TRIGGER!!!!!!!!!"
        return True

    def main(self):
        gtk.main()

if __name__ == "__main__":
    wujaApp = WujaApplication()
    wujaApp.main()

