import argparse
import datetime
import hashlib
import re
import sys

from icalendar import Calendar, Event


TEMPLATE_ZERO_YEARS = "{name} wird geboren"
TEMPLATE_ONE_YEAR = "{name} wird ein Jahr alt"
TEMPLATE_YEARS = "{name} wird {age} Jahre alt"

NOW = datetime.datetime.now()
CURRENT_YEAR = datetime.date.today().year
START_YEAR = CURRENT_YEAR - 1
END_YEAR = CURRENT_YEAR + 2

ICAL_VERSION = "2.0"
PRODID = "-//Birthday Extractor//Birthday Extractor//EN"


class Birthday:
    def __init__(self, name, year, month, day):
        self.name = name
        self.year = year
        self.month = month
        self.day = day


def add_birthday_events(birthday, cal):
    for cur_year in range(START_YEAR, END_YEAR):
        event = get_birthday_event(birthday, cur_year)
        
        if not event:
            continue
        
        cal.add_component(event)


def generate_calendar(birthdays):
    cal = Calendar()
    
    cal.add("prodid", PRODID)
    cal.add("version", ICAL_VERSION)
    
    for birthday in birthdays:
        add_birthday_events(birthday, cal)
    
    return cal


def get_birthday_event(birthday, cur_year):
    summary = get_summary(birthday, cur_year)
    
    if not summary:
        return
    
    date = datetime.date(cur_year, birthday.month, birthday.day)
    
    m = hashlib.md5()
    m.update(summary.encode("utf-8"))
    uid = m.hexdigest()
    
    event = Event()
    event.add("summary", summary)
    event.add("dtstart", date)
    # No end date, as per http://www.innerjoin.org/iCalendar/all-day-events.html
    #event.add("dtend", date + datetime.timedelta(days=1))
    event.add("dtstamp", NOW)
    event.add("transp", "TRANSPARENT")
    event["uid"] = uid
    
    return event


def get_summary(birthday, cur_year):
    age = cur_year - birthday.year
    
    if age < 0:
        return
    elif age == 0:
        template = TEMPLATE_ZERO_YEARS
    elif age == 1:
        template = TEMPLATE_ONE_YEAR
    else:
        template = TEMPLATE_YEARS
    
    summary = template.format(name=birthday.name, age=age)
    
    return summary


def parse_birthdays(data):
    birthdays = []
    
    vcards = Calendar.from_ical(data, multiple=True)
    
    for vcard in vcards:
        birthday = vcard.get("bday")
        name = vcard.get("fn")
        
        if not birthday:
            continue
        
        match = re.search(r"^(\d{4})\-(\d{2})\-(\d{2})$", birthday)
        
        if not match:
            print("{} has an invalid birthday: {}".format(name, birthday), file=sys.stderr)
            continue
        
        year, month, day = match.groups()
        year, month, day = int(year), int(month), int(day)
        
        birthday = Birthday(name, year, month, day)
        birthdays.append(birthday)
    
    return birthdays


def parse_files(filenames):
    birthdays = []
    
    for filename in filenames:
        with open(filename, "r", encoding="utf-8") as fh:
            data = fh.read()
        
        cur_birthdays = parse_birthdays(data)
        birthdays.extend(cur_birthdays)
    
    return birthdays


def main():
    parser = argparse.ArgumentParser(description="Extract birthdays from multiple vCard files into one iCalendar file.")
    parser.add_argument("-i", dest="input", action="append", required=True)
    parser.add_argument("-o", dest="output")
    args = parser.parse_args()
    
    birthdays = parse_files(args.input)
    calendar = generate_calendar(birthdays)
    output_data = calendar.to_ical()
    
    if args.output:
        with open(args.output, "wb") as fh:
            fh.write(output_data)
    else:
        print(output_data.decode("utf-8"))


if __name__ == "__main__":
    main()
