import re
from html import unescape

from ztoe import texts
from ztoe.schedule import SLOTS_PER_DAY

ROW_TAG = "tr"
LIMITS_TAG = "h3"
UPDATED_TAG = "h4"
WHITE_COLORS = {"white", "#fff", "#ffffff"}
QUEUE_PATTERN = re.compile(r"\d+\.\d+")
LINE_BREAK_PATTERN = re.compile(r"<br\s*/?>", re.I)
ANY_TAG_PATTERN = re.compile(r"<[^>]+>")
CELL_PATTERN = re.compile(r"<td([^>]*)>(.*?)</td>", re.S | re.I)
BACKGROUND_PATTERN = re.compile(r"background\s*:\s*([^;\" >]+)", re.I)


def html_to_text(fragment):
    fragment = LINE_BREAK_PATTERN.sub("\n", fragment)
    fragment = unescape(ANY_TAG_PATTERN.sub("", fragment))
    lines = (" ".join(line.split()) for line in fragment.splitlines())
    return "\n".join(line for line in lines if line)


def find_tags(html, tag):
    return re.findall(rf"<{tag}[^>]*>(.*?)</{tag}>", html, re.S | re.I)


def find_tag_texts(html, tag):
    return [html_to_text(content) for content in find_tags(html, tag)]


def find_cells(row):
    return CELL_PATTERN.findall(row)


def find_queue_name(cells):
    for _, content in cells[:-SLOTS_PER_DAY]:
        text = html_to_text(content)
        if QUEUE_PATTERN.fullmatch(text):
            return text
    return None


def has_light(cell_attributes):
    background = BACKGROUND_PATTERN.search(cell_attributes)
    return not background or background.group(1).lower() in WHITE_COLORS


def parse_states(cells):
    return [has_light(attributes) for attributes, _ in cells[-SLOTS_PER_DAY:]]


def parse_schedules(html):
    schedules = []
    for row in find_tags(html, ROW_TAG):
        cells = find_cells(row)
        if len(cells) <= SLOTS_PER_DAY:
            continue

        queue = find_queue_name(cells)
        if not queue:
            continue

        if not schedules or queue in schedules[-1]:
            schedules.append({})
        schedules[-1][queue] = parse_states(cells)

    return schedules


def is_limit_line(line):
    is_period = line.startswith(texts.SITE_LIMITS_PERIOD_PREFIX)
    is_title = texts.SITE_LIMITS_TITLE_MARK in line
    return is_period or is_title


def parse_limits(html):
    limits = []
    for block in find_tag_texts(html, LIMITS_TAG):
        if texts.SITE_LIMITS_MARK in block:
            lines = block.splitlines()
            limits += [line for line in lines if is_limit_line(line)]
    return limits


def parse_updated(html):
    for block in find_tag_texts(html, UPDATED_TAG):
        if block.startswith(texts.SITE_UPDATED_PREFIX):
            updated = block.removeprefix(texts.SITE_UPDATED_PREFIX)
            return updated.strip() or texts.UNKNOWN
    return texts.UNKNOWN


def parse_page(html):
    return {
        "limits": parse_limits(html),
        "updated": parse_updated(html),
        "schedules": parse_schedules(html),
    }
