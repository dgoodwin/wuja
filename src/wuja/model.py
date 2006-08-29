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

""" Model classes for the Wuja application. """

__revision__ = "$Revision$"

import dateutil.rrule
import vobject
import shelve
import os.path

from datetime import datetime
from dateutil.parser import parse
from logging import getLogger

from wuja.data import WUJA_DIR

logger = getLogger("model")

WEEKDAY_MAP = {
    "MO": 0,
    "TU": 1,
    "WE": 2,
    "TH": 3,
    "FR": 4,
    "SA": 5,
    "SU": 6
}


class Cache:

    """
    Maintains the persistence and lookup of calendars.

    Supports save, load, and delete. (if a calendar has changed we
    toss the old and create a new one)
    """

    def __init__(self, db):
        self.__db_file = os.path.join(WUJA_DIR, db)
        logger.info("Opening shelve database: " + self.__db_file)
        self._cache = shelve.open(self.__db_file)

    def has_calendar(self, url):
        return self._cache.has_key(url)

    def save(self, cal_to_save):
        """ Save calendar to disk. """
        # Force users to delete a calendar before they try to resave it:
        if self._cache.has_key(cal_to_save.url):
            raise Exception("Calendar already exists: " + cal_to_save.url)

        logger.debug("Caching calendar: " + cal_to_save.title)
        self._cache[cal_to_save.url] = cal_to_save

    def load(self, url):
        """ Load calendar from disk. """
        cal = self._cache[url]
        logger.debug("Loading calendar: " + cal.title)
        return cal

    def load_all(self):
        """ Load all calendars from disk and return as a list. """
        all_calendars = []
        for url in self._cache.keys():
            all_calendars.append(self._cache[url])
        return all_calendars

    def close(self):
        """ Shutdown this calendar manager. """
        self._cache.close()

    def empty(self):
        """ Delete all calendars from the on-disk cache. """
        for k in self._cache.keys():
            self._cache.pop(k)

    def delete(self, url):
        """ Delete the calendar with the specified url from the database. """
        self._cache.pop(url)


class Calendar:

    """ A representation of a Google Calendar. """

    def __init__(self, title, url, last_update):
        self.title = title
        self.url = url
        self.last_update = last_update
        self.entries = []


class Entry:

    """ Parent class of calendar entries. Consider it abstract. """

    def __init__(self, entry_id, title, desc, remind, location, updated,
            duration):
        self.entry_id = entry_id
        self.title = title
        self.description = desc
        self.location = location
        self.updated = updated
        self.duration = duration
        self.reminder = remind

    def events(self, end_date):
        """ Returns the events for this entry between now and the end date. """
        raise Exception("Not implemented.")


class SingleOccurrenceEntry(Entry):

    """ An entry occurring only once. """

    def __init__(self, entry_id, title, desc, remind, updated, time,
        duration, location):
        Entry.__init__(self, entry_id, title, desc, remind, location,
            updated, duration)
        self.time = time

    def get_events(self, start_date, end_date):
        """
        Returns at most one event for this single occurrence
        calendar entry.
        """
        # Assume a start date of now, no point returning past events:
        if not start_date:
            start_date = datetime.now()
        if end_date < start_date:
            raise BadDateRange, "Your dates are out of order, fool"
        return_me = []
        if start_date <= self.time <= end_date:
            return_me.append(Event(self.time, self))
        return return_me


class RecurringEntry(Entry):

    """
    An entry with recurrence information.

    Note that this object only stores the recurrence text in the database,
    and is parsed on every load/fetch.
    """

    def __init__(self, entry_id, title, desc, remind, location,
        updated, recurrence):
        Entry.__init__(self, entry_id, title, desc, remind, location,
            updated, None)
        self.__parse_recurrence(recurrence)

    def __parse_recurrence(self, recurrence):
        """ Parses the recurrence field. (iCalendar format, see RFC 2445) """
        # Parses only the fields that Google Calendar seems to use, and of
        # those just the ones we're interested in. (Sorry, it's a big spec.)
        parsed = vobject.readOne(recurrence, findBegin=False)

        self.start_date = parse(parsed.dtstart.value)

        # Seems to arrive as something like PT1800S:
        self.duration = None
        if parsed.contents.has_key('duration'):
            self.duration = int(parsed.duration.value[2:-1])

        self.__build_rrule(parsed.rrule.value)

    def __build_rrule(self, rule_text):
        """
        Convert the recurrence data from Google's feed into something
        the dateutil library can work with.
        """
        freq = None

        # Define the same defaults as the rrule constructor takes:
        params = {}
        params['dtstart'] = self.start_date

        for prop in rule_text.split(';'):
            key, val = prop.split('=')
            if key == 'FREQ':
                freq = getattr(dateutil.rrule, val)
            else:
                key = key.lower()
                val = val.split(',')

                # Massage attributes into something dateutil can use:
                if key == 'byday':
                    key = 'byweekday' # documented dateutil deviance from RFC

                    for i in range(len(val)):
                        val[i] = getattr(dateutil.rrule, val[i])

                    val = tuple(val)

                elif key == 'until':
                    val = datetime(int(val[0][0:4]), int(val[0][4:6]),
                        int(val[0][6:8]))

                elif key == 'wkst':
                    val = WEEKDAY_MAP[val[0]]

                else:
                    val = tuple(val)

                params[str(key)] = val

        self.rrule = dateutil.rrule.rrule(freq, **params)

    def get_events(self, start_date, end_date):
        """
        Return a list of all events for this recurring entry
        between the specified start and end date.
        """
        # Assume a start date of now, no point returning past events:
        if start_date == None:
            start_date = datetime.now()

        if end_date < start_date:
            raise BadDateRange, "Your dates are out of order, fool."

        event_list = []
        event_date_times = self.rrule.between(start_date, end_date, inc=True)
        for event_time in event_date_times:
            event_list.append(Event(event_time, self))
        return event_list


class Event:

    """ An actual calendar event. Can be associated with an alarm. """

    def __init__(self, time, entry):
        self.time = time
        self.entry = entry
        self.accepted = False # set true once user confirms event

    def get_key(self):
        """
        Used to simulate an event.key member representing a unique
        string for this event.
        """
        return str(self.entry.entry_id) + str(self.time)

    def set_key(self):
        """
        Dummy setter for the key property, which doesn't really
        exist.
        """
        raise Exception("Keys aren't for setting.")

    key = property(get_key, set_key)


class BadDateRange(Exception):

    """ Exception for messed up date ranges. """

    pass


