# Notes #

This is a [Flask](https://flask.palletsprojects.com/en/3.0.x/) web app.
Static resources (such as JS and CSS files) are in `static/`.
Templates (such as HTML pages that rendered by the server) are in `templates/`.

# Common tasks #

Setup python environment:
``` shell
conda env create -f environment.yaml
conda activate seismic_dataset_viewer
```

Run dev server:
``` shell
flask --app server.py --debug run
```

Run prod server (needs root permissions to bind to port 80):
```shell
sudo sh run_server.sh
```

Install systemd service for prod server (location of systemd files may vary):
``` shell
sudo cp pickhelper.service /etc/systemd/system/
```
