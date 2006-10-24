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
from datetime import datetime

#from wuja.application import find_file_on_path

logger = getLogger("calendar_window")

class CalendarWindow(gobject.GObject):

    def __init__(self, cache):
        gobject.GObject.__init__(self)
        self.cache = cache

        glade_file = 'wuja/data/calendar.glade'
        window_name = 'calendar'
        glade_calendar = gtk.glade.XML(find_file_on_path(glade_file))
        self.calendar_window = glade_calendar.get_widget('calendar')
        self.textview = glade_calendar.get_widget('textview')

        signals = {
            'on_calendar_day_selected': self.display_entries,
        }
        glade_calendar.signal_autoconnect(signals)

        self.calendar_window.show_all()

    def display_entries(self, calendar_widget):
        selected = calendar_widget.get_date()

        # Calendar returns months starting from 0:
        start_date = datetime(selected[0], selected[1] + 1, selected[2])
        end_date = datetime(selected[0], selected[1] + 1, selected[2], 23, 59)

        # Map event times to event objects for sorting:
        events_for_date = {}

        # Scan all our calendars for events on the given date:
        for calendar in self.cache.load_all():
            for entry in calendar.entries:
                for event in entry.get_events(start_date, end_date):
                    # Multiple events could have the same time:
                    if not events_for_date.has_key(event.time):
                        events_for_date[event.time] = []
                    events_for_date[event.time].append(event)

        txt = "Calendar events: " + start_date.strftime("%B %d %Y") + "\n\n"
        keys = events_for_date.keys()
        keys.sort()
        for key in keys:
            for event in events_for_date[key]:
                txt += event.time.strftime("%I:%M%p")
                txt += " - "
                txt += event.entry.title
                txt += " (" + event.entry.calendar.title + ")"
                txt += "\n"
        self.textview.get_buffer().set_text(txt)


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

