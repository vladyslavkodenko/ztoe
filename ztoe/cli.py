import argparse
import sys

from ztoe import texts
from ztoe.config import QUEUES_FILE, load_queues, save_queues, clear_queues
from ztoe.fetch import URL, NETWORK_ERRORS, fetch_html
from ztoe.parser import QUEUE_PATTERN, parse_page
from ztoe.report import print_report

EXIT_INTERRUPTED = 130


def build_arg_parser():
    parser = argparse.ArgumentParser(description=texts.DESCRIPTION)
    parser.add_argument("queues", nargs="*", help=texts.HELP_QUEUES)
    parser.add_argument(
        "-a", "--all", action="store_true", help=texts.HELP_ALL
    )
    parser.add_argument(
        "-s", "--save", action="store_true", help=texts.HELP_SAVE
    )
    parser.add_argument(
        "-r", "--reset", action="store_true", help=texts.HELP_RESET
    )
    return parser


def find_invalid_queues(queues):
    return [queue for queue in queues if not QUEUE_PATTERN.fullmatch(queue)]


def choose_queues(args):
    if args.all:
        return []
    return args.queues or load_queues()


def forget_queues():
    clear_queues()
    print(texts.QUEUES_FORGOTTEN)


def remember_queues(queues):
    save_queues(queues)
    print(texts.QUEUES_SAVED.format(path=QUEUES_FILE), end="\n\n")


def load_page():
    try:
        html = fetch_html()
    except NETWORK_ERRORS as error:
        sys.exit(texts.FETCH_FAILED.format(url=URL, error=error))
    return parse_page(html)


def run():
    parser = build_arg_parser()
    args = parser.parse_args()

    invalid = find_invalid_queues(args.queues)
    if invalid:
        queues = texts.LIST_SEPARATOR.join(invalid)
        parser.error(texts.INVALID_QUEUES.format(queues=queues))

    if args.reset:
        forget_queues()
        if not args.queues:
            return

    if args.save:
        if not args.queues:
            parser.error(texts.SAVE_NEEDS_QUEUES)
        remember_queues(args.queues)

    print_report(load_page(), choose_queues(args))


def main():
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(EXIT_INTERRUPTED)
    except OSError as error:
        sys.exit(texts.FILE_FAILED.format(path=QUEUES_FILE, error=error))
