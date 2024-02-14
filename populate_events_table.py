import json
import sqlite3
from pathlib import Path


# We only need this to populate the events table after we have already made picks.
def get_num_picks(event_id):
    with sqlite3.connect("picks.db") as cur:
        # This count could be off if we have null picks (i.e. a pick was overwritten w/ a null pick).
        res = cur.execute(
            "SELECT COUNT() FROM (SELECT * from picks WHERE event_id = ? GROUP BY channel_id);",
            (event_id,),
        )
        return res.fetchone()[0]


def add_row(event_dir):
    event_id = event_dir.name
    with open(event_dir / "metadata.json", "r") as f:
        event_m = json.load(f)
    with sqlite3.connect("picks.db") as cur:
        cur.execute(
            "INSERT INTO events (event_id, reference_pick_channel_id, trace_start_time, n_reference_picks, n_user_picks) VALUES (?, ?, ?, ?, ?)",
            (
                event_id,
                event_m["reference_channel"],
                event_m["trace_start_time"],
                len(event_m["reference_picks"]),
                get_num_picks(event_id),
            ),
        )


if __name__ == "__main__":
    for event_dir in Path("events").iterdir():
        add_row(event_dir)
