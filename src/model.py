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
            returnMe.append(Event(self.when, self))
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

        self.startDate = parse(parsed.dtstart.value)

        # Seems to arrive as something like PT1800S:
        self.duration = None
        if parsed.contents.has_key('duration'):
            self.duration = int(parsed.duration.value[2:-1])

        self.__buildRrule(parsed.rrule.value)

        return recurrence

    def __buildRrule(self, ruleText):
        freq = None

        # Define the same defaults as the rrule constructor takes:
        params = {}
        params['dtstart'] = self.startDate

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

    def events(self, startDate, endDate):
        # Assume a start date of now, no point returning past events:
        # TODO: Unless they've never been acknowledged...
        if startDate == None:
            startDate = datetime.now()
        if endDate < startDate or endDate < self.startDate:
            return []

        eventList = []
        eventDateTimes = self.rrule.between(startDate, endDate, inc=True)
        for e in eventDateTimes:
            eventList.append(Event(e, self))
        return eventList

class Event:
    """ An actual calendar event. Can be associated with an alarm. """

    def __init__(self, when, entry):
        self.when = when
        self.entry = entry
