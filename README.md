# Demo (slightly outdated) #

![Picking surface events](./pickhelper_demo_short.gif)

# Notes #

This is a [Flask](https://flask.palletsprojects.com/en/3.0.x/) web app.
Static resources (such as JS and CSS files) are in `static/`.
Templates (such as HTML pages that rendered by the server) are in `templates/`.

The information for an event is stored in a directory `events/{event_id}/`.
Each event has `metadata.json` file with the station locations and reference picks.
Each waveform is stored in a NumPy file `{network_code}.{station_code}.{location_code}.{channel_code}.npy`.

The user picks are stored in a SQLite database `picks.db`.
Each user pick has an id of the user that made the pick and a timestamp of when the pick was saved.
User picks are never deleted, they are only superseded by newer picks.

# Common tasks #

Setup python environment:
``` shell
conda env create -f environment.yaml
conda activate pickhelper
```

Download waveforms for events:
```shell
python neighbors.py
```

Run dev server:
``` shell
flask --app server.py --debug run
```

Create empty picks db:
```shell
sqlite3 picks.db < schema.sql
sqlite3 picks.db < event_schema.sql
```

Populate events table:
```shell
python populate_events_table.py
```

Run prod server (needs root permissions to bind to port 80):
```shell
sudo sh run_server.sh
```

Install systemd service for prod server (location of systemd files may vary):
``` shell
sudo cp pickhelper.service /etc/systemd/system/
```
