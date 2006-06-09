import dateutil.rrule
import vobject

from datetime import datetime
from dateutil.rrule import rrule
from dateutil.parser import parse

class Entry:
    """
    Represents a calendar entry. (not event, can involve recurrence and
    thus many events)
    """

    def __init__(self, id, title, desc, where, updated, duration):
        self.id = id
        self.title = title
        self.description = desc
        self.where = where
        self.updated = updated
        self.duration = duration

    def events(self, endDate):
        """ Returns the events for this entry between now and the end date. """
        raise Exception("Not implemented.")

class SingleOccurrenceEntry(Entry):
    """ An entry occurring only once. """

    def __init__(self, id, title, desc, updated, when, duration, where):
        Entry.__init__(self, id, title, desc, where, updated, duration)
        self.when = when

    def events(self, startDate, endDate):
        # Assume a start date of now, no point returning past events:
        # TODO: Unless they've never been acknowledged!!!
        if startDate == None:
            startDate = datetime.now()
        if endDate < startDate:
            return []
        returnMe = []
        if startDate < self.when < endDate:
            returnMe.append(Event(self.when, self.duration, self.where))
        return returnMe

class RecurringEntry(Entry):
    """ An entry with recurrence information. """

    def __init__(self, id, title, desc, where, updated, recurrence):
        Entry.__init__(self, id, title, desc, where, updated, None)
        self.__parseRecurrence(recurrence)

    def __parseRecurrence(self, recurrence):
        """ Parses the recurrence field. (iCalendar format, see RFC 2445) """
        # Parses only the fields that Google Calendar seems to use, and of
        # those just the ones we're interested in. (Sorry, it's a big spec.)
        parsed = vobject.readOne(recurrence)

        d = parsed.dtstart.value
        self.startDate = parse(d)

        # Seems to arrive as something like PT1800S:
        self.duration = int(parsed.duration.value[2:-1])

        self.__buildRrule(parsed.rrule.value)

        return recurrence

    def __buildRrule(self, ruleText):
        freq = None

        # TODO: Find a better way to leverage dynamic keyword arguments:

        # Define the same defaults as the rrule constructor takes:
        params = {}
        params['interval'] = 1
        params['wkst'] = None
        params['count'] = None
        params['until'] = None
        params['bysetpos'] = None
        params['bymonth'] = None
        params['bymonthday'] = None
        params['byyearday'] = None
        params['byeaster'] = None
        params['byweekno'] = None
        params['byweekday'] = None
        params['byhour'] = None
        params['byminute'] = None
        params['bysecond'] = None

        for prop in ruleText.split(';'):
            key, val = prop.split('=')
            if key == 'FREQ':
                freq = getattr(dateutil.rrule, val)
            else:
                key = key.lower()
                val = val.split(',')
                if key == 'byday':
                    key = 'byweekday' # documented dateutil deviance from RFC
                    # Convert "MO, TU, WE..." strings to their rrule objects:
                    for i in range(len(val)):
                        val[i] = getattr(dateutil.rrule, val[i])
                    val = tuple(val)
                elif key == 'until':
                    val = datetime(int(val[0][0:4]), int(val[0][4:6]),
                        int(val[0][6:8]))
                else:
                    val = tuple(val)

                if not params.has_key(key):
                    raise Exception("Unsupported recurrence property: " + key)
                params[key] = val

        self.rrule = rrule(freq, dtstart=self.startDate,
            interval=params['interval'], wkst=params['wkst'],
            count=params['count'], until=params['until'],
            bysetpos=params['bysetpos'], bymonth=params['bymonth'],
            bymonthday=params['bymonthday'], byyearday=params['byyearday'],
            byeaster=params['byeaster'], byweekno=params['byweekno'],
            byweekday=params['byweekday'], byhour=params['byhour'],
            byminute=params['byminute'], bysecond=params['bysecond'])

    def events(self, startDate, endDate):
        # Assume a start date of now, no point returning past events:
        # TODO: Unless they've never been acknowledged...
        if startDate == None:
            startDate = datetime.now()
        if endDate < startDate or endDate < self.startDate:
            return []
        return self.rrule.between(startDate, endDate, inc=True)

class Event:
    """ An actual calendar event. Can be associated with an alarm. """

    def __init__(self, when, duration, where):
        self.when = when
        self.duration = duration
        self.where = where
