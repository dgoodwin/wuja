""" Model classes for the Wuja application. """

__revision__ = "$Revision$"

import dateutil.rrule
import vobject

from datetime import datetime
from dateutil.rrule import rrule
from dateutil.parser import parse
from logging import getLogger

logger = getLogger("model")

class Entry:
    """ Parent class of calendar entries. """

    def __init__(self, id, title, desc, where, updated, duration):
        self.id = id
        self.title = title
        self.description = desc
        self.where = where
        self.updated = updated
        self.duration = duration

    def events(self, end_date):
        """ Returns the events for this entry between now and the end date. """
        raise Exception("Not implemented.")

class SingleOccurrenceEntry(Entry):
    """ An entry occurring only once. """

    def __init__(self, id, title, desc, updated, when, duration, where):
        Entry.__init__(self, id, title, desc, where, updated, duration)
        self.when = when

    def events(self, start_date, end_date):
        """ Returns at most one event for this single occurrence
        calendar entry.
        """
        # Assume a start date of now, no point returning past events:
        if start_date == None:
            start_date = datetime.now()
        if end_date < start_date:
            return []
        return_me = []
        if start_date < self.when < end_date:
            return_me.append(Event(self.when, self))
        return return_me

class RecurringEntry(Entry):
    """ An entry with recurrence information. """

    def __init__(self, id, title, desc, where, updated, recurrence):
        Entry.__init__(self, id, title, desc, where, updated, None)
        self.__parse_recurrence(recurrence)

    def __parse_recurrence(self, recurrence):
        """ Parses the recurrence field. (iCalendar format, see RFC 2445) """
        # Parses only the fields that Google Calendar seems to use, and of
        # those just the ones we're interested in. (Sorry, it's a big spec.)
        parsed = vobject.readOne(recurrence)

        self.start_date = parse(parsed.dtstart.value)

        # Seems to arrive as something like PT1800S:
        self.duration = None
        if parsed.contents.has_key('duration'):
            self.duration = int(parsed.duration.value[2:-1])

        self.__build_rrule(parsed.rrule.value)

        return recurrence

    def __build_rrule(self, ruleText):
        """ Convert the recurrence data from Google's feed into something
        the dateutil library can work with.
        """
        freq = None

        # Define the same defaults as the rrule constructor takes:
        params = {}
        params['dtstart'] = self.start_date

        for prop in ruleText.split(';'):
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

                else:
                    val = tuple(val)

                params[str(key)] = val

        self.rrule = rrule(freq, **params)

    def events(self, start_date, end_date):
        """ Return a list of all events for this recurring entry
        between the specified start and end date.
        """
        # Assume a start date of now, no point returning past events:
        if start_date == None:
            start_date = datetime.now()
        if end_date < start_date or end_date < self.start_date:
            return []

        event_list = []
        event_date_times = self.rrule.between(start_date, end_date, inc=True)
        for e in event_date_times:
            event_list.append(Event(e, self))
        return event_list

class Event:
    """ An actual calendar event. Can be associated with an alarm. """

    def __init__(self, when, entry):
        self.when = when
        self.entry = entry
        self.accepted = False # set true once user confirms event

    def get_key(self):
        """ Used to simulate an event.key member representing a unique
        string for this event.
        """
        return str(self.entry.id) + str(self.when)

    def set_key(self):
        raise Exception("Key's aren't for setting.")

    key = property(get_key, set_key)
