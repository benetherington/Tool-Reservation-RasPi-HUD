from icalendar import Calendar, Event, vDatetime
from datetime import datetime, timezone
from tzlocal import get_localzone
from urllib.request import urlopen

url = "https://calendar.google.com/calendar/ical/ideafablabs%40gmail.com/public/basic.ics"
gcal = Calendar().from_ical(urlopen(url).read().decode('iso-8859-1'))

Now = datetime.now().astimezone(get_localzone())

events = []

for component in gcal.walk():
        if component.name == "VEVENT" and hasattr(component.get('dtstart').dt, "time"):
            events.append( [component.get('dtstart').dt, component.get('dtend').dt, component.get('summary')] )

sorted_events = sorted(events, key= lambda component: component[0])
upcoming_events = list( [tstart, tend, description] for tstart, tend, description in sorted_events if tend > datetime.now().astimezone(get_localzone()) )

if upcoming_events[0][0] < Now:
    current_reservation = upcoming_events[0]
    next_reservation = upcoming_events[1]
else:
    current_reservation = None
    next_reservation = upcoming_events[0]