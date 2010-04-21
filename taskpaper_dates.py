#!/usr/bin/env python
import sys
from taskpaper.taskpaper import *
import parsedatetime.parsedatetime as pdt
import parsedatetime.parsedatetime_consts as pdc
import datetime
from time import mktime

DATE_FORMAT = "%Y-%m-%d"
UPCOMING_DAYS = 2
cal = pdc.Constants()
date_parser = pdt.Calendar(cal)

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
    tasks = tp.filter_by_tag("due")
    for task in tasks:
        if task.tags['due'] == None:
            task.tags['due'] = format_date(datetime.date.today())
        else:
            task.tags['due'] = format_date(parse_date(task.tags['due']))

def add_friendly_tags(tp):
    tasks = tp.filter_by_tag("due")
    for task in tasks:
        clean_tags(task, ('overdue','today','upcoming'))
        today = datetime.date.today()
        try:
            due = parse_date(task.tags['due'])
            if due < today:
                task.tags['overdue'] = None
            elif due == today:
                task.tags['today'] = None
            else:
                td = due - today
                if td.days <= UPCOMING_DAYS:
                    task.tags['upcoming'] = None
        except:
            task.tags['error'] = "invalid date"

def clean_tags(task, tags):
    for tag in tags:
        if task.tags.has_key(tag):
            del task.tags[tag]

def process_repeating(tp):
    tasks = tp.filter_by_tag("repeat")
    for task in tasks:
        if task.tags.has_key("done"):
            due = task.tags['due']
            new_due = parse_date(task.tags['repeat'], parse_date(due).timetuple())
            if not new_due:
                tasks.tags['error'] = 'invalid repeat'
                continue
            task.tags['due'] = format_date(new_due)
            clean_tags(task, ('done',))

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

def main(args):
    url = args[0]
    tp = process_file(url)
    print tp

if __name__ == "__main__": main(sys.argv[1:])
