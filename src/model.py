from datetime import datetime

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
        import vobject
        parsed = vobject.readOne(recurrence)
        #parsed.prettyPrint()
        #print(dir(parsed))
        for child in parsed.getChildren():
            if child.name == 'DURATION':
                # Seems to arrive as something like PT1800S:
                self.duration = int(child.value[2:-1])
#            elif child.name == 'DTSTART':
#                startDate = datetime(
        return recurrence # TODO: Change this...

    def events(self, startDate, endDate):
        # Assume a start date of now, no point returning past events:
        # TODO: Unless they've never been acknowledged!!!
        if startDate == None:
            startDate = datetime.now()
        if endDate < startDate:
            return []
        return []

class Event:
    """ An actual calendar event. Can be associated with an alarm. """

    def __init__(self, when, duration, where):
        self.when = when
        self.duration = duration
        self.where = where
