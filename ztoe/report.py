from datetime import datetime

from ztoe import texts
from ztoe.schedule import (
    SLOT_MINUTES,
    SLOTS_PER_DAY,
    find_next_change,
    find_outages,
    format_outages,
    format_time_left,
    minutes_since_midnight,
    outage_hours,
    slot_at,
    slot_to_time,
)

INDENT = "  "
COLUMN_GAP = "  "
SEPARATOR_CHAR = "-"


def describe_change_time(slot):
    if slot < SLOTS_PER_DAY:
        return slot_to_time(slot)
    return texts.TOMORROW_AT.format(time=slot_to_time(slot - SLOTS_PER_DAY))


def current_status(states, now, tomorrow_states=None):
    states_ahead = states + (tomorrow_states or [])
    current_slot = slot_at(now)
    light = texts.LIGHT_ON if states[current_slot] else texts.LIGHT_OFF

    change_slot = find_next_change(states_ahead, current_slot)
    if change_slot is None:
        return texts.UNTIL_END.format(light=light)

    minutes_left = change_slot * SLOT_MINUTES - minutes_since_midnight(now)
    return texts.UNTIL_CHANGE.format(
        light=light,
        time=describe_change_time(change_slot),
        left=format_time_left(minutes_left),
    )


def build_row(queue, states, status=""):
    if not states:
        return [queue, texts.NOT_IN_TABLE, "", ""]

    outages = find_outages(states)
    times = format_outages(outages) or texts.NO_OUTAGES
    hours = f"{outage_hours(outages):g}"
    return [queue, times, hours, status]


def build_rows(
    selected_queues, states_by_queue, now=None, tomorrow_states_by_queue=None
):
    rows = []
    for queue in selected_queues:
        states = states_by_queue.get(queue)
        status = ""
        if now and states:
            tomorrow_states = (tomorrow_states_by_queue or {}).get(queue)
            status = current_status(states, now, tomorrow_states)
        rows.append(build_row(queue, states, status))
    return rows


def without_empty_last_column(rows):
    if any(row[-1] for row in rows[1:]):
        return rows
    return [row[:-1] for row in rows]


def column_widths(rows):
    return [max(len(cell) for cell in column) for column in zip(*rows)]


def format_line(cells, widths):
    padded = [cell.ljust(width) for cell, width in zip(cells, widths)]
    return (INDENT + COLUMN_GAP.join(padded)).rstrip()


def print_table(rows):
    header, *body = without_empty_last_column([texts.TABLE_HEADER, *rows])
    widths = column_widths([header, *body])
    separator = [SEPARATOR_CHAR * width for width in widths]
    for row in [header, separator, *body]:
        print(format_line(row, widths))


def print_header(page):
    print(texts.UPDATED.format(updated=page["updated"]))


def print_limits(limits):
    if not limits:
        return
    print()
    for line in limits:
        print(line if texts.SITE_LIMITS_TITLE_MARK in line else INDENT + line)


def queue_sort_key(queue):
    return [int(part) for part in queue.split(".")]


def sorted_queues(queues):
    return sorted(queues, key=queue_sort_key)


def queues_to_show(selected_queues, states_by_queue):
    return selected_queues or sorted_queues(states_by_queue)


def print_day(title, rows):
    print(f"\n{title}")
    print_table(rows)


def print_missing_tomorrow():
    print(f"\n{texts.TOMORROW_MISSING}")


def print_report(page, selected_queues):
    now = datetime.now()
    schedules = page["schedules"]
    today = schedules[0] if schedules else None
    tomorrow = schedules[1] if len(schedules) > 1 else None

    print_header(page)
    print_limits(page["limits"])

    if today:
        shown = queues_to_show(selected_queues, today)
        print_day(texts.TODAY, build_rows(shown, today, now, tomorrow))

    if tomorrow:
        shown = queues_to_show(selected_queues, tomorrow)
        print_day(texts.TOMORROW, build_rows(shown, tomorrow))
    else:
        print_missing_tomorrow()
