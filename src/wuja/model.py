""" Model classes for the Wuja application. """

__revision__ = "$Revision$"

import dateutil.rrule
import vobject
import sqlobject

from datetime import datetime
from dateutil.rrule import rrule
from dateutil.parser import parse
from logging import getLogger

logger = getLogger("model")

class SingleOccurrenceEntry(sqlobject.SQLObject):
    """ An entry occurring only once. """
    entry_id = sqlobject.StringCol()
    title = sqlobject.StringCol()
    description = sqlobject.StringCol()
    location = sqlobject.StringCol()
    updated = sqlobject.StringCol()
    duration = sqlobject.IntCol()
    reminder = sqlobject.IntCol()
    feed_title = sqlobject.StringCol()
    time = sqlobject.DateTimeCol()

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
        if start_date < self.time < end_date:
            return_me.append(Event(self.time, self))
        return return_me

class RecurringEntry(sqlobject.SQLObject):
    """ An entry with recurrence information.

    Note that this object only stores the recurrence text in the database,
    and is parsed on every load/fetch.
    """
    entry_id = sqlobject.StringCol()
    title = sqlobject.StringCol()
    description = sqlobject.StringCol()
    reminder = sqlobject.IntCol()
    location = sqlobject.StringCol()
    updated = sqlobject.StringCol()
    feed_title = sqlobject.StringCol()
    recurrence = sqlobject.StringCol()

    def _init(self, *args, **kw):
        sqlobject.SQLObject._init(self, *args, **kw)
        self.__parse_recurrence(self.recurrence)

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

    def __build_rrule(self, rule_text):
        """ Convert the recurrence data from Google's feed into something
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
        """ Used to simulate an event.key member representing a unique
        string for this event.
        """
        return str(self.entry.entry_id) + str(self.time)

    def set_key(self):
        """ Dummy setter for the key property, which doesn't really
        exist.
        """
        raise Exception("Keys aren't for setting.")

    key = property(get_key, set_key)
