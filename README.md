birthday_extractor.py
=====================
This Python program takes multiple [vCard](https://en.wikipedia.org/wiki/VCard) files,
parses the birthdays of people it finds there and creates a calendar file in the
[iCalendar](https://en.wikipedia.org/wiki/ICalendar) format.

I use it to get a calendar with the birthdays of my contacts I store in
[Radicale](http://radicale.org/). So you might want to run this program in regular
intervals.

Requirements
------------
1. Python
 * Tested with Python 3.4 only.
1. [icalendar](https://pypi.python.org/pypi/icalendar)

Installation
------------
1. `pip install -r requirements.txt`

Usage
-----
`python birthday_extractor.py -i contacts.vcf -o birthdays.ical`

The `-i` option can be specified multiple times. If you do not specifiy the
`-o` option, the output will be printed to `stdout`.
