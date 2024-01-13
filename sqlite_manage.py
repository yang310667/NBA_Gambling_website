import sqlite3

# 連線到 SQLite 資料庫
with sqlite3.connect("D:\研究所\資料庫\project1\DBMS\Gamble.db") as con:
    cur = con.cursor()

    # 將 TEXT 型態欄位轉換為 DATE 型態
    cur.execute("ALTER TABLE single_match RENAME TO single_match_old")  # 先將原始表格更名為 Member_info_old
    cur.execute("CREATE TABLE single_match (matchId TEXT, home TEXT,away TEXT,date DATE);")  # 建立新的表格

    # 將原始資料從 Member_info_old 複製到新的 Member_info 表格
    cur.execute("INSERT INTO single_match SELECT matchId, home, away, date(date) FROM single_match_old")

    # 刪除原始表格
    cur.execute("DROP TABLE single_match_old")

    con.commit()
