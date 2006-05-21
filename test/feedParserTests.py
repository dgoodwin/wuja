import unittest
import settestpath

from feedparser import FeedParser

xml = """<?xml version='1.0' encoding='UTF-8'?><feed xmlns='http://www.w3.org/2005/Atom' xmlns:openSearch='http://a9.com/-/spec/opensearchrss/1.0/' xmlns:gd='http://schemas.google.com/g/2005'><id>http://www.google.com/calendar/feeds/gqfbp7ajq1b71v5jgdtbe815ps%40group.calendar.google.com/private-f404480fd9b64f2f7cb78b2a3d6daf6a/full</id><updated>2006-05-18T15:24:44.000Z</updated><title type='text'>Wuja Testing Calendar</title><subtitle type='text'>Sample google calendar events for the purposes of Wuja development. Should include atleast one event of every possible type we can come up with.</subtitle><link rel='http://schemas.google.com/g/2005#feed' type='application/atom+xml' href='http://www.google.com/calendar/feeds/gqfbp7ajq1b71v5jgdtbe815ps%40group.calendar.google.com/private-f404480fd9b64f2f7cb78b2a3d6daf6a/full'></link><link rel='self' type='application/atom+xml' href='http://www.google.com/calendar/feeds/gqfbp7ajq1b71v5jgdtbe815ps%40group.calendar.google.com/private-f404480fd9b64f2f7cb78b2a3d6daf6a/full?max-results=25'></link><link rel='next' type='application/atom+xml' href='http://www.google.com/calendar/feeds/gqfbp7ajq1b71v5jgdtbe815ps%40group.calendar.google.com/private-f404480fd9b64f2f7cb78b2a3d6daf6a/full?start-index=26&amp;max-results=25'></link><author><name>Devan Goodwin</name><email>dcgoodwin@gmail.com</email></author><generator version='1.0' uri='http://www.google.com/calendar'>Google Calendar</generator><openSearch:itemsPerPage>25</openSearch:itemsPerPage><gd:where valueString=''></gd:where><entry><id>http://www.google.com/calendar/feeds/gqfbp7ajq1b71v5jgdtbe815ps%40group.calendar.google.com/private-f404480fd9b64f2f7cb78b2a3d6daf6a/full/no9kpfn2eb5p7pksum3uft0mas</id><published>2006-05-18T10:00:00.000Z</published><updated>2006-05-18T15:24:41.000Z</updated><category scheme='http://schemas.google.com/g/2005#kind' term='http://schemas.google.com/g/2005#event'></category><title type='text'>Standup Meeting</title><content type='text'>Meet to discuss progress and why you aren't doing a better job.</content><link rel='alternate' type='text/html' href='http://www.google.com/calendar/event?eid=bm85a3BmbjJlYjVwN3Brc3VtM3VmdDBtYXNfMjAwNjA1MThUMTMwMDAwWiBncWZicDdhanExYjcxdjVqZ2R0YmU4MTVwc0Bncm91cC5jYWxlbmRhci5nb29nbGUuY29t' title='alternate'></link><link rel='self' type='application/atom+xml' href='http://www.google.com/calendar/feeds/gqfbp7ajq1b71v5jgdtbe815ps%40group.calendar.google.com/private-f404480fd9b64f2f7cb78b2a3d6daf6a/full/no9kpfn2eb5p7pksum3uft0mas'></link><author><name>Wuja Testing Calendar</name></author><gd:recurrence>DTSTART;TZID=Canada/Atlantic:20060518T100000
DURATION:PT1800S
RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
BEGIN:VTIMEZONE
TZID:Canada/Atlantic
X-LIC-LOCATION:Canada/Atlantic
BEGIN:STANDARD
TZOFFSETFROM:-0300
TZOFFSETTO:-0400
TZNAME:AST
DTSTART:19701025T020000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
END:STANDARD
BEGIN:DAYLIGHT
TZOFFSETFROM:-0400
TZOFFSETTO:-0300
TZNAME:ADT
DTSTART:19700405T020000
RRULE:FREQ=YEARLY;BYMONTH=4;BYDAY=1SU
END:DAYLIGHT
END:VTIMEZONE
</gd:recurrence><gd:transparency value='http://schemas.google.com/g/2005#event.opaque'></gd:transparency><gd:eventStatus value='http://schemas.google.com/g/2005#event.confirmed'></gd:eventStatus><gd:where valueString='Boardroom'></gd:where></entry></feed>
"""

class ParsingTests(unittest.TestCase):

    def testSimpleParsing(self):
        feedParser = FeedParser(xml)
        events = feedParser.events()
        self.assertEqual(1, len(events))

def suite():
    return unittest.makeSuite(ParsingTests)

if __name__ == "__main__":
    unittest.main(defaultTest="suite")
