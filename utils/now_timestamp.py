import time


def get_timestamp_from_now(days: int):
    return int(time.time()) * 1000 + (days * 24 * 60 * 60 * 1000)


def get_now_timestamp():
    return get_timestamp_from_now(0)
