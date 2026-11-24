from ztoe import texts

MINUTES_PER_HOUR = 60
MINUTES_PER_DAY = 24 * MINUTES_PER_HOUR
SLOT_MINUTES = 30
SLOTS_PER_DAY = MINUTES_PER_DAY // SLOT_MINUTES


def minutes_since_midnight(moment):
    return moment.hour * MINUTES_PER_HOUR + moment.minute


def slot_at(moment):
    return minutes_since_midnight(moment) // SLOT_MINUTES


def slot_to_time(slot):
    hours, minutes = divmod(slot * SLOT_MINUTES, MINUTES_PER_HOUR)
    return texts.CLOCK_TIME.format(hours=hours, minutes=minutes)


def format_time_left(minutes):
    if minutes < MINUTES_PER_HOUR:
        return texts.MINUTES.format(minutes=minutes)
    hours, minutes = divmod(minutes, MINUTES_PER_HOUR)
    return texts.HOURS_AND_MINUTES.format(hours=hours, minutes=minutes)


def find_outages(states):
    outages, start = [], None
    for slot, has_light in enumerate(states + [True]):
        if not has_light and start is None:
            start = slot
        elif has_light and start is not None:
            outages.append((start, slot))
            start = None
    return outages


def format_time_range(start, end):
    return texts.TIME_RANGE.format(
        start=slot_to_time(start), end=slot_to_time(end)
    )


def format_outages(outages):
    ranges = [format_time_range(start, end) for start, end in outages]
    return texts.LIST_SEPARATOR.join(ranges)


def outage_hours(outages):
    outage_slots = sum(end - start for start, end in outages)
    return outage_slots * SLOT_MINUTES / MINUTES_PER_HOUR


def find_next_change(states, from_slot):
    for slot in range(from_slot + 1, len(states)):
        if states[slot] != states[from_slot]:
            return slot
    return None
