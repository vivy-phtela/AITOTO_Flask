import sqlite3

#データベース読み込み
db = sqlite3.connect(
    "instance/test.db",
    isolation_level=None,
)

#テーブルを削除
sql = """DROP TABLE employee"""

db.execute(sql)
db.close()