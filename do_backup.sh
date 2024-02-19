cd /home/ec2-user/pickhelper
/home/ec2-user/miniconda3/envs/pickhelper/bin/python backup_db.py
aws s3 cp picks_backup.db "s3://picksbackup/picks_backup_$(date -u +'%Y-%m-%d-%H-%M-%S')"
