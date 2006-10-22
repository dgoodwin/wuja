#   Wuja - Google Calendar (tm) notifications for the GNOME desktop.
#
#   Copyright (C) 2006 Devan Goodwin <dgoodwin@dangerouslyinc.com>
#   Copyright (C) 2006 James Bowes <jbowes@dangerouslyinc.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#   02110-1301  USA

""" The Wuja calendar display window. """

__revision__ = "$Revision$"


import pygtk
pygtk.require('2.0')

import gtk
import gtk.glade
import gobject
import os
import os.path
import sys

from logging import getLogger

#from wuja.application import find_file_on_path

logger = getLogger("calendar_window")

class CalendarWindow(gobject.GObject):

    def __init__(self):
        gobject.GObject.__init__(self)
        logger.debug('Opening calendar window.')

        glade_file = 'wuja/data/calendar.glade'
        window_name = 'calendar'
        glade_calendar = gtk.glade.XML(find_file_on_path(glade_file))
        calendar_window = glade_calendar.get_widget('calendar')

        signals = {
            'on_calendar_day_selected': self.display_entries,
            'on_button_press': self.display_entries,
        }
        glade_calendar.signal_autoconnect(signals)

        calendar_window.show_all()

    def display_entries(self, calendar_widget):
        logger.debug("Changed calendar day.")
        logger.debug(calendar_widget.get_date())


# FIXME: Had to duplicate this, import from wuja.application wasn't working.
def find_file_on_path(pathname):
    """
    Scan the Python path and locate a file with the given name.

    See:
      http://www.linuxjournal.com/xstatic/articles/lj/0087/4702/4702l2.html
    """
    if os.path.isabs(pathname):
        return pathname
    for dirname in sys.path:
        candidate = os.path.join(dirname, pathname)
        if os.path.isfile(candidate):
            return candidate
    raise Exception("Could not find %s on the Python path."
        % pathname)

