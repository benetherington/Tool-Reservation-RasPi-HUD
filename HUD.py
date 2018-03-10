# These do not come with Raspbien and need to be installed
from icalendar import Calendar, Event, vDatetime
from tzlocal import get_localzone

from datetime import datetime, timezone, timedelta
from math import floor
from urllib.request import urlopen
from tkinter import *

url = "https://calendar.google.com/calendar/ical/ideafablabs%40gmail.com/public/basic.ics"
max_request_interval = 5*60
last_request_time  = datetime.now() - timedelta(seconds=max_request_interval)
last_obtained_data = ""

def poll_gcalendar():
    '''
    Downloads ICS file from Google Calendar, and returns it as a string. Limits HTTP requests to Google.
    '''
    global last_request_time
    if datetime.now()-last_request_time > timedelta(seconds=max_request_interval):               # only pull data from the internet if it's been longer than the interval.
        global last_obtained_data
        last_obtained_data = Calendar().from_ical(urlopen(url).read().decode('iso-8859-1'))
        last_request_time  = datetime.now()
        print("sent HTTP request to gcal") 
    return last_obtained_data

def get_reservations():
    '''
    Asks for the list of calendar events, parses them, sorts them and returns the most helpful.

    Returns a dict for the current reservation and the next reservation, which are dicts of the beginning time, ending time and description.
    Returns None for the first if there`s no reservation in effect.
    '''
    calendar = poll_gcalendar()
    events = []
    for component in calendar.walk():                                               # parse events
        if component.name == "VEVENT" and hasattr(component.get('dtstart').dt, "time"):
            events.append( [component.get('dtstart').dt, component.get('dtend').dt, component.get('summary')] )
    sorted_events = sorted(events, key= lambda component: component[0])             # sort events
    upcoming_events = list( {'start': tstart, 'end': tend, 'name': tsummary} for tstart, tend, tsummary in sorted_events if tend > datetime.now().astimezone(get_localzone()) ) # discard events in the past, build a list for those in the future. Weird 't' prependatures to not use keyword 'end'
    if upcoming_events[0]['start'] < datetime.now().astimezone(get_localzone()):    # Decide if there's a current reservation or not
        current_reservation = upcoming_events[0]                                    # TODO: parse summary to just retain user's name
        next_reservation = upcoming_events[1]
    else:
        current_reservation = None
        next_reservation = upcoming_events[0]
    return {"current": current_reservation, "next": next_reservation}

def hour_min(date_time):
    '''
    Returns a tidy string for a given datetime or timedelta.

    Returns hour:minute for datetimes, XX days for long timedeltas and hour:minute:second for short ones.
    '''
    if type(date_time).__name__ == "datetime":
        return str(date_time.astimezone(get_localzone()).hour)+":"+str('{:02d}'.format(date_time.minute))
    elif type(date_time).__name__ == "timedelta":
        if date_time.days>1:
            return str(date_time.days)+" days"
        else:
            return str(floor(date_time.total_seconds()/3600))+":"+str('{:02d}'.format(floor( (date_time.total_seconds()/60)%60 )))+":"+str('{:02d}'.format(floor( date_time.total_seconds()%60 )))

class App:
    def __init__(self, master):
        self.master = master
        master.geometry("800x480")

        # HEADER
        header = LabelFrame(master, text="IFL Tool Reservation HUD")
        header.grid(row=0, column=0, columnspan=2, sticky=N+S+E+W)
        Label(header, text="Universal Laser").grid( row=1, column=0, columnspan=2)
        # CONTENT
        current = LabelFrame(master, bd=3, relief=RAISED)
        current.grid(row=2, column=1, columnspan=2)
        upcoming = LabelFrame(master, bd=3, relief=RAISED)
        upcoming.grid(row=3, column=1, columnspan=2)
        # FOOTER
        Label(master, text="Don't pretend you didn't know.®", font=("arial", 9)).grid(row=4, column=2)
        # BEHAVIORS
        self.clear_display(current)
        self.update_current(current)
        self.clear_display(upcoming)
        self.update_upcoming(upcoming)

    def update_current(self, target):
        if get_reservations()["current"]: # Display if someone's currently on the tool
            target.config( text="In use" )
            Label( target,  text=hour_min( get_reservations()["current"]["end"]-datetime.now().astimezone(get_localzone()) ), font=("arial", 20)).grid(row=0)
            Label(target, text=get_reservations()["current"]['name']+' until '+hour_min(get_reservations()['current']['end']) ).grid(row=1)
        else:                             # Display if the tool is free
            target.config( text="Free to use!" )
            Label( target, text=hour_min( get_reservations()["next"]["start"]-datetime.now().astimezone(get_localzone()) ), font=("arial", 20) ).grid(   row=1, column=0)

        self.master.after(1000, self.update_current, target)

    def update_upcoming(self, target):
        target.config( text="Upcoming reservations" )
        Label( target, text="Next user: "+get_reservations()["next"]['name']+" at "+hour_min(get_reservations()["next"]['start']) ).grid(                 row=2, column=0)
        self.master.after(10000, self.update_upcoming, target)

    def clear_display(self, target):
        for widget in target.winfo_children():
            widget.destroy()
        self.master.after(100000, self.clear_display, target)

root = Tk()

app = App(root)

root.mainloop()















