#!/usr/bin/env python
import sys
#from taskpaper.taskpaper import *
import parsedatetime.parsedatetime as pdt
import parsedatetime.parsedatetime_consts as pdc
import datetime
from time import mktime
import re

DATE_FORMAT = "%Y-%m-%d"
UPCOMING_DAYS = 2
cal = pdc.Constants()
date_parser = pdt.Calendar(cal)

class Task(object):
    """
    >>> t = Task("- Test Task @home @due(today) wooo")
    >>> print t.is_task()
    True
    >>> print t.has_tag("home")
    True
    >>> print t.has_tag("due")
    True
    >>> print t.has_tag("woooo")
    False
    >>> print t.get_tag_value('due')
    today
    >>> t.add_tag("next")
    >>> print t
    - Test Task @home @due(today) wooo @next
    >>> t.add_tag("repeat", "sunday")
    >>> print t
    - Test Task @home @due(today) wooo @next @repeat(sunday)
    >>> t.set_tag_value('due', '2010-04-21')
    >>> print t
    - Test Task @home @due(2010-04-21) wooo @next @repeat(sunday)
    >>> t.set_tag_value('due', '2010-04-21')
    >>> print t.get_tag_value('due')
    2010-04-21
    >>> t2 = Task("Project:")
    >>> t2.is_task()
    False
    >>> t.remove_tag('next')
    >>> print t
    - Test Task @home @due(2010-04-21) wooo @repeat(sunday)
    >>> t.remove_tag('repeat')
    >>> print t
    - Test Task @home @due(2010-04-21) wooo

    """
    def __init__(self, line):
        self.line = line

    def is_task(self):
        return (self.line.lstrip("\t")[0] == "-") if len(self.line) != 0 else False

    def has_tag(self, tag_name):
        return (self.line.find("@%s"% tag_name) != -1)

    def add_tag(self, tag, value = None):
        self.line += " @%s" % tag
        if value:
            self.line += "(%s)" % value

    def get_tag_value(self, tag_name):
        matches = re.compile("@%s\((.*?)\)" % tag_name).findall(self.line)
        return matches[0] if len(matches) != 0 else None

    def set_tag_value(self, tag_name, value):
        self.line = re.sub("@%s.*?\)" % tag_name, "@%s(%s)" % (tag_name, value), self.line)

    def remove_tag(self, tag_name):
        if self.get_tag_value(tag_name):
            self.line = re.sub(" @%s.*?\)" % tag_name, "", self.line)
        else:
            self.line = re.sub(" @%s" % tag_name, "", self.line)

    def __str__(self):
        return self.line


def format_date(date):
    return date.strftime(DATE_FORMAT)

def parse_date(date_string, initial = None):
    """
    print parse_date("2010-04-01")
    datetime.datetime(2010, 4, 1, 0, 0)
    """
    if date_string.find("-") != -1:
        return datetime.datetime.strptime(date_string, DATE_FORMAT).date()
    else:
        struct = date_parser.parse(date_string, initial)
        if struct[1] == 1:
            return datetime.date.fromtimestamp(mktime(struct[0]))
        else:
            return None

def change_friendly_dates(tp):
    """
    """
    if tp.has_tag("due"):
        val = tp.get_tag_value('due')
        if val == None:
            tp.set_tag_value('due', format_date(datetime.date.today()))
        else:
            tp.set_tag_value('due', format_date(parse_date(val)))

def add_friendly_tags(tp):
    if tp.has_tag('due'):
        clean_tags(tp, ('overdue','today','upcoming'))
        today = datetime.date.today()
        try:
            due = parse_date(tp.get_tag_value('due'))
            if due < today:
                tp.add_tag('overdue')
            elif due == today:
                tp.add_tag('today')
            else:
                td = due - today
                if td.days <= UPCOMING_DAYS:
                    tp.add_tag('upcoming')
        except:
            tp.add_tag('error', 'invalid date')

def clean_tags(task, tags):
    for tag in tags:
        if task.has_tag(tag):
            task.remove_tag(tag)

def process_repeating(tp):
    if tp.has_tag('repeat'):
        if tp.has_tag("done"):
            due = tp.get_tag_value('due')
            repeat = tp.get_tag_value('repeat')
            new_due = parse_date(repeat, parse_date(due).timetuple())
            if not new_due:
                tp.add_tag('error', 'invalid repeat')
                return
            tp.set_tag_value('due', format_date(new_due))
            clean_tags(tp, ('done',))

def process_file(url):
    tp = parse_taskpaper(url)
    return process_tp(tp)

def process_tp(tp):
    change_friendly_dates(tp)
    process_repeating(tp)
    add_friendly_tags(tp)
    return tp

def process_string(tp_string):
    tp = parse_taskpaper_from_string(tp_string)
    return process_tp(tp)

def parse(taskpaper_string):
    lines = taskpaper_string.split('\n')
    new_file = []
    for line in lines:
        t = Task(line)
        if t.is_task():
            change_friendly_dates(t)
            process_repeating(t)
            add_friendly_tags(t)
        new_file.append(str(t))
    return '\n'.join(new_file)

def main(args):
    url = args[0]
    f = open(url)
    tp_string = f.read()
    f.close()
    print tp_string
    tp = parse(tp_string)
    print tp

if __name__ == "__main__": main(sys.argv[1:])
