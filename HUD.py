from icalendar import Calendar, Event, vDatetime
from datetime import datetime, timezone, timedelta
from tzlocal import get_localzone
from urllib.request import urlopen
from tkinter import *

url = "https://calendar.google.com/calendar/ical/ideafablabs%40gmail.com/public/basic.ics"
max_request_interval = 5*60
last_request_time  = datetime.now() - timedelta(seconds=max_request_interval)
last_obtained_data = ""

def poll_gcalendar():
    '''
    Downloads ICS file from Google Calendar, and returns it as a string.
    '''

    global last_request_time
    # print("last_request_time: " + str(last_request_time))
    # print("last_request_time delta:" + str(last_request_time+timedelta(seconds=max_request_interval)))
    # print("now:                    " + str(datetime.now()))
    # print("delta delta: " + str(last_request_time+timedelta(seconds=max_request_interval) - datetime.now()))
    if datetime.now()-last_request_time > timedelta(seconds=max_request_interval):               # only pull data from the internet if it's been longer than the interval.
        global last_obtained_data
        last_obtained_data = Calendar().from_ical(urlopen(url).read().decode('iso-8859-1'))
        last_request_time  = datetime.now()
        print("sent HTTP request to gcal")
        
    return last_obtained_data

def get_reservations():
    '''
    sorts them and returns the most helpful.

    Returns a dict for the current reservation and the next reservation, which are an array of the beginning time, ending time and description.
    Returns None for the first if there`s no reservation in effect.
    '''

    calendar = poll_gcalendar()
    events = []

    for component in calendar.walk():
        if component.name == "VEVENT" and hasattr(component.get('dtstart').dt, "time"):
            events.append( [component.get('dtstart').dt, component.get('dtend').dt, component.get('summary')] )

    sorted_events = sorted(events, key= lambda component: component[0]) # sort events
    upcoming_events = list( {'start': tstart, 'end': tend, 'name': tsummary} for tstart, tend, tsummary in sorted_events if tend > datetime.now().astimezone(get_localzone()) ) # discard events in the past, build a list for those in the future. Weird 't' prependatures to not use keyword 'end'

    if upcoming_events[0]['start'] < datetime.now().astimezone(get_localzone()):    # Decide if there's a current reservation or not
        current_reservation = upcoming_events[0]                                    # TODO: parse summary to just retain user's name
        next_reservation = upcoming_events[1]
    else:
        current_reservation = None
        next_reservation = upcoming_events[0]

    return {"current": current_reservation, "next": next_reservation}
    # return {"current": None, "next": ["next start", "next end", "next description"]}

def hour_min(date_time): #TODO: add relative date if this is too far in the future
    return str(date_time.hour)+":"+str('{:02d}'.format(date_time.minute))

class App:
    def __init__(self, master):
        # HEADER
        Label(master, text="IFL Tool Reservation HUD").grid(row=0, column=0, sticky=W)
        Label(master, text="Universal Laser").grid(         row=1, column=0, sticky=W)

        if get_reservations()["current"]: # Display if someone's currently on the tool
            Label( master, text="Current user:"+get_reservations()["current"][2] ).grid(                                          row=2, column=1)
            Label( master, text="00:00:00" ).grid(                                                                                row=3, column=1)
            Label( master, text="Next user: "+get_reservations()["next"][2]+" at "+hour_min(get_reservations()["next"][0]) ).grid(row=4, column=1)
        else:                             # Display if the tool is free
            Label( master, text="Free use" ).grid(                                                                                row=2, column=1)
            Label( master, text="00:00:00" ).grid(                                                                                row=3, column=1)
            Label( master, text="Next user: "+get_reservations()["next"][2]+" at "+hour_min(get_reservations()["next"][0]) ).grid(row=4, column=1)


root = Tk()

app = App(root)

root.mainloop()















