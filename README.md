# Demo #

![Picking surface events](./pickhelper_demo.gif)

# Notes #

Setup python environment:
``` shell
conda env create -f environment.yaml
conda activate pickhelper
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

Run production server (need to install stuff first):
```shell
sudo /home/ec2-user/miniconda3/envs/pickhelper/bin/mod_wsgi-express start-server wsgi.py --port 80 --user ec2-user --group ec2-user --host 0.0.0.0
```
