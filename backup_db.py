import sqlite3

if __name__ == "__main__":
    src = sqlite3.connect("picks.db")
    dst = sqlite3.connect("picks_backup.db")
    with dst:
        src.backup(dst)
    src.close()
    dst.close()
