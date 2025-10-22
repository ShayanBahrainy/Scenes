import datetime

def get_time() -> int:
    "Returns the current Unix time."
    return int(datetime.datetime.now(datetime.UTC).timestamp())


def max_length(string: str, length: int) -> str:
    "If the `string` is longer than `length`, it's cut down to `length`"
    if len(string) <= length:
        return string

    return string[:length-3] + "..."
