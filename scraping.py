import datetime


def parse_utc_timestamp(timestamp: str) -> datetime.datetime:
    """2025-01-28T03:22:32.149Z -> datetime"""
    date, time = timestamp.split("T")
    time = time.split(".")[0]
    yyyy, mm, dd = date.split("-")
    hh, minute, ss = time.split(":")
    return datetime.datetime(int(yyyy), int(mm), int(dd), int(hh), int(minute), int(ss), tzinfo=datetime.timezone.utc).astimezone()

if __name__ == "__main__":
    print(parse_utc_timestamp("2025-01-28T03:22:32.149Z").astimezone().strftime("%Y-%m-%d"))