from pathlib import Path

FILE_ENCODING = "utf-8"


def config_dir():
    return Path.home() / ".config" / "ztoe"


QUEUES_FILE = config_dir() / "queues"


def load_queues():
    try:
        return QUEUES_FILE.read_text(encoding=FILE_ENCODING).split()
    except FileNotFoundError:
        return []


def save_queues(queues):
    QUEUES_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUEUES_FILE.write_text("\n".join(queues) + "\n", encoding=FILE_ENCODING)


def clear_queues():
    QUEUES_FILE.unlink(missing_ok=True)
