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

import pygtk
pygtk.require('2.0')

import gtk
import gtk.glade
import gobject

from logging import getLogger
from datetime import datetime,timedelta
from dateutil.tz import tzlocal

from wuja.utils import find_file_on_path

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
            'on_calendar_month_change': self.mark_month
        }
        glade_calendar.signal_autoconnect(signals)

        self.calendar_window.show_all()
        self.update_text_for_date(datetime.now(tzlocal()))
        self.mark_month(self.calendar_window)


    def mark_month(self,calendar_window):
        """
        Marks every date that has an entry this month.
        """
        # Prepare first and last date in this month, a bit awkward:
        # Get current month from the calendar widget:
        year, month, day = calendar_window.get_date()
        start_date = datetime(year,month + 1, 1, tzinfo=tzlocal())
        tmp_date = start_date + timedelta(days=31)
        end_date = datetime(tmp_date.year, tmp_date.month, 1,
            tzinfo=tzlocal()) - timedelta(days=1)

        # Freeze to reduce flicker:
        calendar_window.freeze()
        calendar_window.clear_marks()

        # Find all entries and mark them:
        for calendar in self.cache.load_all():
            for entry in calendar.entries:
                map(
                     lambda e: calendar_window.mark_day(e.time.day),
                     entry.get_events_starting_between(start_date, end_date)
                   )

        calendar_window.thaw()

    def display_entries(self, calendar_widget):
        selected = calendar_widget.get_date()

        # Calendar returns months starting from 0:
        query_date = datetime(selected[0], selected[1] + 1, selected[2],
            tzinfo=tzlocal())
        self.update_text_for_date(query_date)

    def update_text_for_date(self, query_date):

        # Map event times to event objects for sorting:
        events_for_date = {}
        logger.debug("Displaying calendar for: " + str(query_date))

        # Scan all our calendars for events on the given date:
        for calendar in self.cache.load_all():
            for entry in calendar.entries:
                for event in entry.get_events_occurring_on(query_date):
                    # Multiple events could have the same time:
                    if not events_for_date.has_key(event.time):
                        events_for_date[event.time] = []
                    events_for_date[event.time].append(event)

        txt = "Calendar events: " + query_date.strftime("%B %d %Y") + "\n\n"
        keys = events_for_date.keys()
        keys.sort()
        for key in keys:
            for event in events_for_date[key]:

                # Display all-day events differently:
                if event.time.hour == 0 and event.time.minute == 0 \
                    and event.entry.duration % 86400 == 0:
                    txt += "ALL DAY"
                else:
                    txt += event.time.strftime("%I:%M%p")

                txt += " - "
                txt += event.entry.title
                txt += " (" + event.entry.calendar.title + ")"
                txt += "\n"
        self.textview.get_buffer().set_text(txt)


