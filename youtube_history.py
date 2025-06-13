import argparse
import json
from datetime import datetime, timedelta, timezone
from typing import List, Tuple


def load_events(path: str) -> List[Tuple[datetime, str, str]]:
    """Load watch history events from a Takeout JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    events = []
    for entry in data:
        if "title" not in entry or "time" not in entry:
            continue

        title = entry["title"]
        if title.startswith("Watched "):
            title = title.replace("Watched ", "", 1)

        channel = "Unknown"
        if entry.get("subtitles") and isinstance(entry["subtitles"], list):
            channel = entry["subtitles"][0].get("name", channel)

        time_str = entry["time"].replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(time_str)
        except ValueError:
            continue

        events.append((dt, title, channel))
    return events


def main(path: str) -> None:
    events = load_events(path)
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(days=7)

    for dt, title, channel in events:
        if dt >= start_time:
            print(f"[{dt.strftime('%d-%m-%y')}] {title} {channel}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="List YouTube videos watched in the last 7 days"
    )
    parser.add_argument(
        "path", help="Path to the Google Takeout watch-history.json file"
    )
    args = parser.parse_args()
    main(args.path)
