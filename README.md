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
```
