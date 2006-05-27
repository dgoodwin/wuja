from datetime import datetime

class Entry:
    """
    Represents a calendar entry. (not event, can involve recurrence and
    thus many events)
    """

    def __init__(self, id, title, desc, updated, duration):
        self.id = id
        self.title = title
        self.description = desc
        self.updated = updated
        self.duration = duration

    def events(self, endDate):
        """ Returns the events for this entry between now and the end date. """
        raise Exception("Not implemented.")

class SingleOccurrenceEntry(Entry):
    """ An entry occurring only once. """

    def __init__(self, id, title, desc, updated, when, duration, where):
        Entry.__init__(self, id, title, desc, updated, duration)
        self.when = when
        self.where = where

    def events(self, endDate):
        # Assume a start date of now, no point returning past events:
        # TODO: Unless they've never been acknowledged!!!
        startDate = datetime.now()

        returnMe = []
        if startDate < self.when < endDate:
            returnMe.append(Event(self.when, self.duration, self.where))
        return returnMe

class RecurringEntry(Entry):
    """ An entry with recurrence information. """

    def __init__(self, id, title, desc, updated, recurrence):
        Entry.__init__(self, id, title, desc, updated, None)
        self.recurrence = recurrence

    def events(self, endDate):
        return []

class Event:
    """ An actual calendar event. Can be associated with an alarm. """
    def __init__(self, when, duration, where):
        self.when = when
        self.duration = duration
        self.where = where
