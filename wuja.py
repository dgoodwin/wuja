#!/usr/bin/env python

import pygtk
import gtk
from egg import trayicon

icon = gtk.image_new_from_stock(gtk.STOCK_HOME, gtk.ICON_SIZE_BUTTON)

tray_thing = trayicon.TrayIcon("wuja")
tray_thing.add(icon)

tray_thing.show_all()

gtk.main()
