from icalendar import Calendar, Event, vDatetime
from datetime import datetime, timezone
from urllib.request import urlopen


url = "https://calendar.google.com/calendar/ical/ideafablabs%40gmail.com/public/basic.ics"
gcal = Calendar().from_ical(urlopen(url).read().decode('iso-8859-1'))

upcoming_events = []

for component in gcal.walk():
        if component.name == "VEVENT" and hasattr(component.get('dtstart').dt, "time"):
            upcoming_events.append( [component.get('dtstart').dt, component.get('summary')] )
            # print(component.get('summary'))
            # print(component.get('dtstart').dt)
            # print(component.get('dtend'))
            # print(component.get('dtstamp'))

sorted_events = sorted(upcoming_events, key= lambda component: component[0])

print(list( time for time, description in sorted_events if time > datetime.now(tz=timezone.utc) ))