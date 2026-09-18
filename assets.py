import re
import jdatetime


def parse_jalali_datetime(value):
    date_part, time_part = value.split()

    date_parts = list(map(int, re.split(r"[/.\-]", date_part)))
    time_parts = list(map(int, time_part.split(":")))

    if len(str(date_parts[0])) == 4:
        year, month, day = date_parts
    else:
        day, month, year = date_parts

    hour, minute, second = time_parts

    dt = jdatetime.datetime(
        year,
        month,
        day,
        hour,
        minute,
        second
    )

    base = jdatetime.datetime(1, 1, 1)

    return (dt - base).total_seconds() / 86400