daily_recurrence = """DTSTART;TZID=Canada/Atlantic:20060518T100000
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
END:VTIMEZONE"""

daily_recurrence_for_one_week = """DTSTART;TZID=Canada/Atlantic:20060605T130000
DURATION:PT3600S
RRULE:FREQ=DAILY;UNTIL=20060610T003000Z
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
END:VTIMEZONE"""

weekly_recurrence_all_day = """DTSTART;VALUE=DATE:20060605
DTEND;VALUE=DATE:20060606
RRULE:FREQ=WEEKLY;BYDAY=MO
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
END:VTIMEZONE"""
