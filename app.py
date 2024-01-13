from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import datetime
import random
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
import os

app = Flask(__name__)

totime = datetime.datetime.now()
con = sqlite3.connect("Gamble.db")
# print("Database opened successfully")
# con.execute("create table Employees (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, address TEXT NOT NULL)")
# print("Table created successfully")

# 會員登入的設定
app.secret_key = app.config.get("flask", "yangyang")
login_manager = LoginManager(app)
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message = "請證明你是賭鬼"


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


@login_manager.user_loader
def user_loader(userpig):
    user = User(userpig)
    return user


@login_manager.request_loader
def request_loader(userpig):
    user = User(userpig)
    return user


# 首頁
@app.route("/")
def index():
    logged_in = False
    session.clear()
    login_manager.init_app
    return render_template("index.html", logged_in=logged_in)


@app.route("/index_in")
@login_required
def index_in():
    logged_in = True
    return render_template(
        "index_in.html", logged_in=logged_in, user_id=current_user.id
    )


# 加入會員網頁
@app.route("/add")
def add():
    return render_template("add.html")


# 加入會員後送出的動作
@app.route("/savedetails", methods=["POST"])
def saveDetails():
    if request.method == "POST":
        try:
            memberId = request.form["memberId"]
            password = request.form["password"]
            birthday = request.form["birthday"]
            identity = request.form["identity"]
            accounts = request.form["account"]
            with sqlite3.connect("Gamble.db") as con:
                cur = con.cursor()
                cur.execute(
                    "INSERT into member_info(memberId,password,birthday,identity,account) values (?,?,?,?,?)",
                    (memberId, password, birthday, identity, accounts),
                )
                con.commit()

        except:
            con.rollback()
            flash("輸入有問題")
        finally:
            return render_template("success_add.html", user_id=memberId)
            con.close()


# 比賽資訊網頁
@app.route("/view")
def view():
    # 辨認是否登入
    logged_in = False
    if "username" in session:
        logged_in = True
    return render_template("view_index.html", logged_in=logged_in)


# 單場比賽資訊網頁
@app.route("/view2")
def view2():
    # 辨認是否登入
    logged_in = False
    if "username" in session:
        logged_in = True

    con = sqlite3.connect("Gamble.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM match_info WHERE `賽事種類` = '單場賽場' Order By date;")
    con.commit()
    rows = cur.fetchall()
    return render_template("view2.html", rows=rows, logged_in=logged_in)


# 系列賽比賽資訊網頁
@app.route("/view3")
def view3():
    # 辨認是否登入
    logged_in = False
    if "username" in session:
        logged_in = True

    con = sqlite3.connect("Gamble.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("Select * from match_info WHERE `賽事種類` = '系列賽' Order By date")
    rows = cur.fetchall()
    con.close()
    return render_template("view2.html", rows=rows, logged_in=logged_in)


# NBA球隊資訊
@app.route("/team")
def team():
    # 辨認是否登入
    logged_in = False
    if "username" in session:
        logged_in = True

    con = sqlite3.connect("Gamble.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("Select * from NBA_playoff_teams  ")
    rows = cur.fetchall()
    con.close()
    return render_template("team.html", rows=rows, logged_in=logged_in)


# NBA球員資訊
@app.route("/player")
def player():
    # 辨認是否登入
    logged_in = False
    if "username" in session:
        logged_in = True

    con = sqlite3.connect("Gamble.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("Select * from NBA_playoff_players  ")
    rows = cur.fetchall()
    con.close()

    return render_template("player.html", rows=rows, logged_in=logged_in)


# 登入網頁
@app.route("/login")
def login():
    return render_template("login.html")


# 登戶會員後的動作
@app.route("/login_result", methods=["POST"])
def login_Result():
    # 辨認是否登入
    username = request.form["memberId"]
    session["username"] = username
    logged_in = False
    if "username" in session:
        logged_in = True

    con = sqlite3.connect("Gamble.db")
    cur = con.cursor()

    if "memberId" in request.form and "password" in request.form:
        memberId = request.form["memberId"]
        password = request.form["password"]

        cur.execute(
            "Select * From Member_info Where memberId = ? and password = ?",
            (memberId, password),
        )
        result = cur.fetchone()
        if result:
            user = user_loader(memberId)
            login_user(user)
            return render_template(
                "index_in.html", user_id=current_user.id, logged_in=logged_in
            )
        else:
            flash("登入失敗了...")
    return redirect("/login")
    con.close()


@app.route("/logout")
def logout():
    users = current_user.id
    session.pop("username", None)
    session.clear()
    logout_user()
    return render_template("logout.html", user=users)


# 出入金的網頁
@app.route("/money_in_out")
@login_required
def money_in_out():
    # 再次查詢更新後的 member_info
    user = current_user.id
    return render_template("money_in_out.html", user=user)


# 出入金成功的網頁
@app.route("/money_add", methods=["POST"])
@login_required
def money_add():
    con = sqlite3.connect("Gamble.db")
    cur = con.cursor()

    action = request.form["action"]
    in_out_money = int(request.form["money"])
    password = request.form["password"]
    user_id = current_user.id

    if action == "deposit":
        cur.execute(
            "UPDATE member_info SET money = money + ? WHERE password = ? AND memberId = ?",
            (in_out_money, password, user_id),
        )
        action_text = "儲值"
        in_out_text = "進入"
    elif action == "withdraw":
        cur.execute(
            "SELECT money FROM member_info WHERE password = ? AND memberId = ?",
            (password, user_id),
        )
        current_money = cur.fetchone()[0]
        if current_money < in_out_money:
            error_message = "錯誤：提領金額超過帳戶餘額"
            return render_template(
                "money_in_out_error.html", error_message=error_message
            )

        cur.execute(
            "UPDATE member_info SET money = money - ? WHERE password = ? AND memberId = ?",
            (in_out_money, password, user_id),
        )
        action_text = "提領"
        in_out_text = "出"
    con.commit()

    # 再次查詢更新後的 member_info
    cur.execute(
        "SELECT money FROM member_info WHERE password = ? AND memberId = ?",
        (password, user_id),
    )
    updated_money = cur.fetchone()[0]

    # 插入操作紀錄到 money_records 資料表中
    user_id = current_user.id
    cur.execute(
        "INSERT INTO money_records (user_id, action, amount) VALUES (?, ?, ?)",
        (user_id, action_text, in_out_money),
    )
    con.commit()
    con.close()

    return render_template(
        "money_in_out_success.html",
        money=in_out_money,
        user=current_user.id,
        action=action_text,
        in_out=in_out_text,
        updated_money=updated_money,  # 傳遞更新後的 money
    )


# 出入金紀錄
@app.route("/money_in_out_record")
@login_required
def money_in_out_record():
    con = sqlite3.connect("Gamble.db")
    cur = con.cursor()

    user_id = current_user.id

    # 查詢 money_records 表格中屬於當前使用者的紀錄
    cur.execute(
        "SELECT action, amount, created_at FROM money_records WHERE user_id = ?",
        [user_id],
    )
    records = cur.fetchall()
    con.close()

    return render_template("money_in_out_record.html", records=records)


@app.route("/gameplay")
def gameplay():
    logged_in = False
    con = sqlite3.connect("Gamble.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    curr = con.cursor()
    cur.execute(
        "SELECT * FROM match_info WHERE date > DATE('2023-04-18') AND date = (SELECT date FROM match_info WHERE date > DATE('2023-04-18') Order By date asc);"
    )
    con.commit()
    rows = cur.fetchall()
    curr.execute("SELECT * FROM bet WHERE gametype = '單場賽事'; ")
    con.commit()
    results = curr.fetchall()
    con.close()

    return render_template(
        "gameplay_view2.html", rows=rows, results=results, logged_in=logged_in
    )


# 下注網頁
@app.route("/bet_index")
@login_required
def bet_index():
    user = current_user.id
    return render_template("bet_index.html")


@app.route("/bet1")
@login_required
def bet1():
    con = sqlite3.connect("Gamble.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    date = "2023-04-18"
    cur.execute(
        "SELECT bet.matchId, match_info.home, match_info.away, bet.gametype, bet.gamble, bet.line FROM bet,match_info where gametype = '單場賽事' and match_info.matchId=bet.matchId and gametype = '單場賽事' and date > DATE('2023-04-18') and date = (SELECT date FROM match_info WHERE date > DATE('2023-04-18') Order By date asc);"
    )
    rows = cur.fetchall()
    con.close()

    return render_template("bet1.html", rows=rows)


@app.route("/bet2")
def bet2():
    con = sqlite3.connect("Gamble.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    date = "2023-04-15"
    cur.execute(
        "SELECT bet.matchId,match_info.home,match_info.away,bet.gametype,bet.gamble,bet.line FROM bet,match_info where match_info.matchId=bet.matchId and gametype = '系列賽' and date > DATE('2023-04-15') and date = (SELECT date FROM match_info WHERE date > DATE('2023-04-15') Order By date asc);"
    )
    rows = cur.fetchall()
    con.close()

    return render_template("bet2.html", rows=rows)


# 下注金額頁面(單場賽事)
@app.route("/bet1_in", methods=["POST"])
@login_required
def bet1_in():
    con = sqlite3.connect("Gamble.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    user_id = current_user.id
    single = request.form["single"]
    project = request.form["project"]
    money = int(request.form["money"])
    password = request.form["password"]

    cur.execute("select money FROM member_info WHERE password = ?", (password,))
    current_money = cur.fetchone()[0]
    cur.execute(
        "UPDATE member_info SET money = money - ? WHERE password = ?", (money, password)
    )
    cur.execute("SELECT money FROM member_info WHERE password = ?", (password,))
    updated_money = cur.fetchone()[0]
    cur.execute(
        "SELECT bet.line*? FROM bet where bet.matchId=? and bet.gamble=? and bet.gametype = '單場賽事'",
        (money, single, project),
    )
    bet_win_money = cur.fetchone()[0]
    cur.execute(
        "INSERT INTO member_record (memberId, 賽事編號, 種類, 下注金額, 可獲得金額,中獎結果) VALUES (?, ?, ?,?,?,?)",
        (user_id, single, project, money, bet_win_money,"未開獎"),
    )
    con.commit()
    con.close()

    return render_template(
        "bet_success.html",
        money=money,
        updated_money=updated_money,
        user=current_user.id,
        bet_win_money=bet_win_money,
    )


# 下注金額頁面(系列賽)
@app.route("/bet2_in", methods=["POST"])
@login_required
def bet2_in():
    con = sqlite3.connect("Gamble.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    user_id = current_user.id
    single = request.form["single"]
    project = request.form["project"]
    money = int(request.form["money"])
    password = request.form["password"]

    cur.execute("select money FROM member_info WHERE password = ?", (password,))
    current_money = cur.fetchone()[0]
    cur.execute(
        "UPDATE member_info SET money = money - ? WHERE password = ?", (money, password)
    )
    cur.execute("SELECT money FROM member_info WHERE password = ?", (password,))
    updated_money = cur.fetchone()[0]
    cur.execute(
        "SELECT bet.line*? FROM bet where bet.matchId=? and bet.gamble=? and bet.gametype = '系列賽'",
        (money, single, project),
    )
    bet_win_money = cur.fetchone()[0]
    cur.execute(
        "INSERT INTO member_record (memberId, 賽事編號, 種類, 下注金額, 可獲得金額,中獎結果) VALUES (?, ?, ?, ?, ?,?)",
        (user_id, single, project, money, bet_win_money,"未開獎" ),
    )
    con.commit()
    con.close()

    return render_template(
        "bet_success.html",
        money=money,
        updated_money=updated_money,
        user=current_user.id,
        bet_win_money=bet_win_money,
    )


# 會員資料
@app.route("/member_infor")
@login_required
def member_infor():
    con = sqlite3.connect("Gamble.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    user_id = current_user.id

    cur.execute("select money FROM member_info WHERE memberId = ?", (user_id,))
    current_money = cur.fetchone()[0]

    cur.execute(
        "select count(id) FROM money_records WHERE user_id=? AND action='儲值'",
        (user_id,),
    )
    in_money_time = cur.fetchone()[0]

    cur.execute(
        "select count(id) FROM money_records WHERE user_id=? AND action='提領'",
        (user_id,),
    )
    out_money_time = cur.fetchone()[0]

    cur.execute("select count(id) FROM member_record WHERE memberId=?", (user_id,))
    gamble_time = cur.fetchone()[0]

    con.close()
    return render_template(
        "member_infor.html",
        user_id=user_id,
        current_money=current_money,
        in_money_time=in_money_time,
        out_money_time=out_money_time,
        gamble_time=gamble_time,
    )


# 會員資料下注紀錄查詢
@app.route("/bet_record")
@login_required
def bet_record():
    con = sqlite3.connect("Gamble.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    user_id = current_user.id

    # 設置日期
    date = "2023-04-17"

    cur.execute(
        """
    SELECT
        member_record.id,
        member_record.賽事編號,
        member_record.種類,
        member_record.下注金額,
        member_record.可獲得金額,
        member_record.中獎結果,
        match_info.date
    FROM
        member_record
    LEFT JOIN
        match_info
    ON
        member_record.賽事編號 = match_info.matchId
    WHERE
        memberId=?
    """,
        (user_id,),
    )

    rows = cur.fetchall()
    i=0
    # 遍历查询结果并调整中獎結果
    for row in rows:
        bet_date = row["date"]
        result = row["中獎結果"]

        if result == '已領獎':
        # 判断是否需要调整中獎結果
            continue
        else:
            if bet_date <= date:
                # 随机选择一半概率调整中獎結果
                random.seed( i )
                if random.random() < 0.5:
                    result = "已中獎"
                else:
                    result = "未中獎"
        i+=1
        # 更新中獎結果到数据库
        cur.execute(
            "UPDATE member_record SET 中獎結果=? WHERE id=?",
            (result, row["id"]),
        )
    con.commit()
    con.close()

    return render_template("bet_record.html", rows=rows,d=date)


# 刪除下注紀錄
@app.route("/delete_record", methods=["POST"])
@login_required
def delete_record():
    data = request.get_json()
    bet_id = data["betId"]
    # 連接資料庫並刪除對應記錄
    con = sqlite3.connect("Gamble.db")
    cur = con.cursor()
    cur.execute("update member_info SET money = money + 下注金額 from (SELECT 下注金額 from member_record where id = ?)",(bet_id, ))
    cur.execute("DELETE FROM member_record WHERE id=?", (bet_id,))
    con.commit()
    con.close()

    return ("Record deleted successfully")


# 操作中獎介面
@app.route("/operate_win")
@login_required
def operate_win():
    user = current_user.id
    return render_template("operate_win.html")


# 發放獎金
@app.route("/operate_success", methods=["POST"])
@login_required
def operate_success():
    con = sqlite3.connect("Gamble.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    user_id = current_user.id
    single = request.form["single"]
    project = request.form["project"]
    cur.execute(
        "UPDATE member_info SET money = money + t.可獲得金額 FROM (SELECT mr.memberId, SUM(mr.可獲得金額) AS 可獲得金額 FROM member_record mr WHERE mr.賽事編號 = ? AND mr.種類 = ? AND mr.中獎結果 = '已中獎' GROUP BY mr.memberId) t WHERE member_info.memberId= t.memberId",
        (single, project),
    )
    cur.execute(
        "UPDATE member_record SET 中獎結果 = ? WHERE 賽事編號 = ? AND 種類 = ?",
        ("已領獎", single, project),
    )
    con.commit()
    con.close()
    return render_template("operate_success.html", single=single, project=project)


if __name__ == "__main__":
    app.run(debug=True)
