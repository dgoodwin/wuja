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

from datetime import datetime, timedelta
from dateutil.tz import tzlocal, gettz
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

    def sync(self):
        self._cache.sync()


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

    key = property(get_key)


class BadDateRange(Exception):

    """ Exception for messed up date ranges. """

    pass


class Calendar:

    """ A representation of a Google Calendar. """

    def __init__(self, title, url, last_update, timezone):
        self.title = title
        self.url = url
        self.last_update = last_update
        self.entries = []
        self.timezone = timezone # string like 'America/Halifax'


class Entry:

    """ Parent class of calendar entries. Consider it abstract. """

    def __init__(self, entry_id, title, desc, remind, location, updated,
            duration, cal):
        self.entry_id = entry_id
        self.title = title
        self.description = desc
        self.location = location
        self.updated = updated
        self.duration = duration
        self.reminder = remind
        self.calendar = cal
        self.exceptions = []

    def get_events_starting_between(self, start_date, end_date):
        """
        Returns the events for this entry starting between the given
        datetimes.
        """
        raise Exception("Not implemented.")

    def get_events_occurring_on(self, date):
        """ Return the events occurring on or throughout the given date. """
        raise Exception("Not implemented.")

    def _event_occurs_on(self, event, duration, query_date):
        """
        Checks if the given event occurs on the date queried.

        Used by both single occurrence and recurring entries.
        """
        start_of_query_date = datetime(query_date.year, query_date.month,
            query_date.day, tzinfo=query_date.tzinfo)
        end_of_query_date = datetime(query_date.year, query_date.month,
            query_date.day, 23, 59, 59, tzinfo=query_date.tzinfo)

        # Removing one second from the duration here to prevent problems
        # with calendar events that claim to end on the first second of the
        # next day instead of the last second of the actual day.
        event_end_time = event.time + timedelta(seconds=duration - 1)

        return_me = []
        # Does the event start within the queried date:
        if start_of_query_date <= event.time <= end_of_query_date:
            return True

        # Does the event end within the queried date:
        elif start_of_query_date <= event_end_time <= end_of_query_date:
            return True

        # Does the event overlap the queried date:
        # NOTE: The <='s below might need some more thought:
        elif event.time <= start_of_query_date and end_of_query_date <= \
            event_end_time:
            return True

        # Event must not occur on the queried date:
        return False


class SingleOccurrenceEntry(Entry):

    """ An entry occurring only once. """

    def __init__(self, entry_id, title, desc, remind, updated, time,
        duration, location, cal):
        Entry.__init__(self, entry_id, title, desc, remind, location,
            updated, duration, cal)
        self.time = time

    def get_debug_info(self):
        """ Returns a string of debug information for this entry. """
        return_str = self.title
        return_str += " / "
        return_str += "time = " + str(self.time)
        return_str += " / "
        return_str += "duration = " + str(self.duration)
        return return_str

    def get_events_starting_between(self, start_date, end_date):
        """
        Returns at most one event for this single occurrence
        calendar entry.
        """
        # Assume a start date of now, no point returning past events:
        if not start_date:
            start_date = datetime.now(tzlocal())
        if end_date < start_date:
            raise BadDateRange, "Your dates are out of order, fool"
        return_me = []
        if start_date <= self.time <= end_date:
            return_me.append(Event(self.time, self))
        return return_me

    def get_events_occurring_on(self, date):
        """ Return the events occurring on or throughout the given date. """
        event = Event(self.time, self)
        return_me = []
        if self._event_occurs_on(event, self.duration, date):
            return_me.append(event)
        return return_me


class RecurringEntry(Entry):

    """
    An entry with recurrence information.

    Note that this object only stores the recurrence text in the database,
    and is parsed on every load/fetch.
    """

    def __init__(self, entry_id, title, desc, remind, location,
        updated, recurrence, cal):
        Entry.__init__(self, entry_id, title, desc, remind, location,
            updated, None, cal)
        self.__parse_recurrence(recurrence)

    def get_debug_info(self):
        """ Returns a string of debug information for this entry. """
        return self.title

    def __parse_recurrence(self, recurrence):
        """ Parses the recurrence field. (iCalendar format, see RFC 2445) """
        # Parses only the fields that Google Calendar seems to use, and of
        # those just the ones we're interested in. (Sorry, it's a big spec.)
        parsed = vobject.readOne(recurrence, findBegin=False)

        # If the recurrence specifies a timezone, use it, otherwise default
        # to the calendar's timezone:
        tz = None
        if parsed.dtstart.params.has_key('TZID'):
            logger.debug("Got timezone from recurrence: " +
                parsed.dtstart.params['TZID'][0])
            tz = gettz(parsed.dtstart.params['TZID'][0])
        else:
            logger.debug("Got timezone from calendar: " +
                self.calendar.timezone)
            tz = gettz(self.calendar.timezone)

        # Timezone info isn't being returned by this call to parse, so for now
        # we'll copy the date and include it ourselves:
        temp_date = parse(parsed.dtstart.value)
        self.start_date = datetime(temp_date.year, temp_date.month,
            temp_date.day, temp_date.hour, temp_date.minute, temp_date.second,
            temp_date.microsecond, tzinfo=tz)

        # Seems to arrive as something like PT1800S:
        self.duration = None

        if parsed.contents.has_key('duration'):
            self.duration = int(parsed.duration.value[2:-1])
        else:
            dtstart = parsed.contents['dtstart'][0].value
            start_date = datetime(int(dtstart[0:4]), int(dtstart[4:6]),
                int(dtstart[6:8]), tzinfo=tz)

            dtend = parsed.contents['dtend'][0].value
            end_date = datetime(int(dtend[0:4]), int(dtend[4:6]),
                int(dtend[6:8]), tzinfo=tz)

            duration = end_date - start_date
            self.duration = (duration.days * 60 * 60 * 24) + duration.seconds

        self.__build_rrule(parsed.rrule.value, tz)

    def __build_rrule(self, rule_text, tz):
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
                        int(val[0][6:8]), tzinfo=tz)

                elif key == 'wkst':
                    val = WEEKDAY_MAP[val[0]]

                elif key == 'count' or key == 'interval':
                    val = int(val[0])

                else:
                    val = tuple(val)

                params[str(key)] = val

        self.rrule = dateutil.rrule.rrule(freq, **params)

    def get_events_starting_between(self, start_date, end_date):
        """
        Return a list of all events for this recurring entry
        between the specified start and end date.
        """
        # Assume a start date of now, no point returning past events:
        if start_date == None:
            start_date = datetime.now(tzlocal())

        if end_date < start_date:
            raise BadDateRange, "Your dates are out of order, fool."

        event_list = []
        event_date_times = self.rrule.between(start_date, end_date, inc=True)
        for event_time in event_date_times:
            if event_time not in self.exceptions:
                event_list.append(Event(event_time, self))
        return event_list

    def get_events_occurring_on(self, date):
        """ Return the events occurring on or throughout the given date. """
        return_me = []

        # Check each possible event that could start or end in this range:
        start_range = datetime(date.year, date.month, date.day,
            tzinfo=tzlocal()) - timedelta(seconds=self.duration)
        end_range = datetime(date.year, date.month, date.day, 23, 59, 59,
            tzinfo=tzlocal()) + timedelta(seconds=self.duration)

        # Do any events start within the queried date:
        possible_events = self.rrule.between(start_range, end_range,
            inc=True)
        for time in possible_events:
            event = Event(time, self)
            if self._event_occurs_on(event, self.duration, date):
                return_me.append(event)

        return return_me


