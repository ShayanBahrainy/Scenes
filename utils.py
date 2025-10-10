import datetime

def get_time() -> int:
    return int(datetime.datetime.now(datetime.UTC).timestamp())
