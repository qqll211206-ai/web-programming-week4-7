"""A small Flask/SQLite campus board. Set SECRET_KEY before starting."""
import functools
import os
import re
import secrets
import sqlite3
from pathlib import Path

import click
from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE = Path(__file__).resolve().parent
secret = os.environ.get("SECRET_KEY")
if not secret:
    raise RuntimeError("Set the SECRET_KEY environment variable before starting.")
app = Flask(__name__, instance_path=str(BASE / "instance"))
app.config.update(
    SECRET_KEY=secret,
    DATABASE=os.environ.get("WEEK7_DATABASE", str(BASE / "instance" / "app.db")),
    SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("APP_HTTPS") == "1",
    MAX_CONTENT_LENGTH=64 * 1024,
)
BOARD_TITLE = "캠퍼스 한 줄 이야기"
BOARD_QUESTION = "오늘 캠퍼스에서 발견한 작은 기쁨이나 바라는 점을 들려주세요."


def get_db():
    if "db" not in g:
        db = sqlite3.connect(app.config["DATABASE"], timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        g.db = db
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    db = get_db()
    db.executescript((BASE / "schema.sql").read_text(encoding="utf-8"))
    # Support the simple user/comment schema of the earlier stages without dropping rows.
    columns = {row["name"] for row in db.execute("PRAGMA table_info(users)")}
    for name in ("is_admin", "is_banned", "is_test"):
        if name not in columns:
            db.execute(f"ALTER TABLE users ADD COLUMN {name} INTEGER NOT NULL DEFAULT 0")
    columns = {row["name"] for row in db.execute("PRAGMA table_info(comments)")}
    if "created_at" not in columns:
        db.execute("ALTER TABLE comments ADD COLUMN created_at TEXT NOT NULL DEFAULT ''")
        db.execute("UPDATE comments SET created_at = CURRENT_TIMESTAMP WHERE created_at = ''")
    # Preserve historical reports even if an older schema did not define UNIQUE.
    db.execute("""CREATE TRIGGER IF NOT EXISTS reports_no_duplicate BEFORE INSERT ON reports
        WHEN EXISTS (SELECT 1 FROM reports WHERE comment_id = NEW.comment_id AND user_id = NEW.user_id)
        BEGIN SELECT RAISE(ABORT, 'duplicate report'); END""")
    db.commit()


@app.cli.command("init-db")
def init_db_command():
    init_db()
    click.echo("Database initialized; existing data was preserved.")


@app.cli.command("promote-admin")
def promote_admin():
    username = os.environ.get("WEEK7_ADMIN_USERNAME", "").strip()
    if not username:
        raise click.ClickException("Set WEEK7_ADMIN_USERNAME.")
    db = get_db()
    cur = db.execute("UPDATE users SET is_admin = 1 WHERE username = ?", (username,))
    if not cur.rowcount:
        raise click.ClickException("Register this user before promoting it.")
    db.commit()
    click.echo("Administrator role granted.")


@app.cli.command("ensure-admin")
def ensure_admin():
    username = os.environ.get("WEEK7_ADMIN_USERNAME", "").strip()
    password = os.environ.get("WEEK7_ADMIN_PASSWORD", "")
    if not re.fullmatch(r"[A-Za-z0-9_]{3,32}", username) or len(password) < 12:
        raise click.ClickException("Set an administrator username and a dedicated password of at least 12 characters.")
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if user is None:
        db.execute("INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)", (username, generate_password_hash(password)))
    elif not user["is_admin"]:
        # Never promote a pre-existing account solely by matching its name.
        if not check_password_hash(user["password_hash"], password):
            raise click.ClickException("Existing account password does not match; role unchanged.")
        db.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (user["id"],))
    elif not check_password_hash(user["password_hash"], password):
        raise click.ClickException("Existing administrator password does not match the environment.")
    db.commit()
    click.echo("Administrator account verified.")


@app.before_request
def load_user_and_check_csrf():
    user_id = session.get("user_id")
    g.user = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone() if user_id is not None else None
    if user_id is not None and g.user is None:
        session.clear()
    if request.method == "POST":
        expected = session.get("csrf_token", "")
        actual = request.form.get("csrf_token", "")
        if not expected or not secrets.compare_digest(expected.encode("utf-8"), actual.encode("utf-8")):
            abort(400)


@app.context_processor
def common():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return {"csrf_token": session["csrf_token"], "board_title": BOARD_TITLE, "board_question": BOARD_QUESTION}


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        if g.user["is_banned"]:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None or g.user["is_banned"] or not g.user["is_admin"]:
            abort(403)
        return view(*args, **kwargs)
    return wrapped


@app.get("/")
def index():
    return redirect(url_for("comments"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not re.fullmatch(r"[A-Za-z0-9_]{3,32}", username) or not 8 <= len(password) <= 128:
            flash("아이디는 영문·숫자·밑줄 3~32자, 비밀번호는 8~128자로 입력해 주세요.")
        else:
            try:
                db = get_db()
                db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, generate_password_hash(password)))
                db.commit()
                flash("가입이 완료되었습니다. 로그인해 주세요.")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("이미 사용 중인 아이디입니다.")
    return render_template("auth.html", mode="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = get_db().execute("SELECT * FROM users WHERE username = ?", (request.form.get("username", "").strip(),)).fetchone()
        if user is None or not check_password_hash(user["password_hash"], request.form.get("password", "")):
            flash("아이디 또는 비밀번호를 확인해 주세요.")
        elif user["is_banned"]:
            flash("이 계정은 현재 이용이 제한되어 있습니다.")
        else:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("comments"))
    return render_template("auth.html", mode="login")


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("comments"))


@app.route("/comments", methods=["GET", "POST"])
def comments():
    db = get_db()
    if request.method == "POST":
        if g.user is None:
            return redirect(url_for("login"))
        if g.user["is_banned"]:
            abort(403)
        content = request.form.get("content", "").strip()
        if not 1 <= len(content) <= 300 or "\n" in content or "\r" in content:
            flash("한 줄 메시지는 1~300자로 입력해 주세요.")
        else:
            # A write transaction makes the per-account rate check and insert atomic.
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM post_events WHERE created_at < datetime('now', '-1 minute')")
            count = db.execute("SELECT COUNT(*) FROM post_events WHERE user_id = ? AND created_at >= datetime('now', '-1 minute')", (g.user["id"],)).fetchone()[0]
            if count >= 3:
                db.rollback()
                flash("1분에 세 개까지 작성할 수 있습니다. 잠시 후 다시 시도해 주세요.")
            else:
                db.execute("INSERT INTO comments (user_id, content, created_at) VALUES (?, ?, CURRENT_TIMESTAMP)", (g.user["id"], content))
                db.execute("INSERT INTO post_events (user_id, created_at) VALUES (?, CURRENT_TIMESTAMP)", (g.user["id"],))
                db.commit()
                return redirect(url_for("comments"))
    rows = db.execute("SELECT c.*, u.username FROM comments c JOIN users u ON u.id = c.user_id ORDER BY c.id DESC").fetchall()
    return render_template("comments.html", comments=rows)


def delete_comment_rows(db, comment_id):
    # Explicit child deletion also supports older databases without cascade clauses.
    db.execute("DELETE FROM reports WHERE comment_id = ?", (comment_id,))
    db.execute("DELETE FROM comments WHERE id = ?", (comment_id,))


@app.post("/comments/<int:comment_id>/delete")
@login_required
def delete_comment(comment_id):
    db = get_db()
    row = db.execute("SELECT user_id FROM comments WHERE id = ?", (comment_id,)).fetchone()
    if row is None:
        abort(404)
    if row["user_id"] != g.user["id"] and not g.user["is_admin"]:
        abort(403)
    delete_comment_rows(db, comment_id)
    db.commit()
    return redirect(request.referrer if request.referrer and request.referrer.startswith(request.host_url + "admin") and g.user["is_admin"] else url_for("comments"))


@app.post("/comments/<int:comment_id>/report")
@login_required
def report(comment_id):
    db = get_db()
    comment = db.execute("SELECT user_id FROM comments WHERE id = ?", (comment_id,)).fetchone()
    if comment is None:
        abort(404)
    if comment["user_id"] == g.user["id"]:
        abort(403)
    reason = request.form.get("reason", "").strip()
    if not 1 <= len(reason) <= 200 or "\n" in reason or "\r" in reason:
        flash("신고 이유를 한 줄로 1~200자 입력해 주세요.")
    else:
        try:
            db.execute("INSERT INTO reports (comment_id, user_id, reason) VALUES (?, ?, ?)", (comment_id, g.user["id"], reason))
            db.commit()
            flash("신고가 접수되었습니다.")
        except sqlite3.IntegrityError:
            flash("이미 신고한 글입니다.")
    return redirect(url_for("comments"))


@app.get("/admin")
@admin_required
def admin():
    db = get_db()
    query = request.args.get("q", "").strip()[:200]
    reported = request.args.get("reported") == "1"
    # instr/lower avoids treating user input as LIKE wildcards.
    rows = db.execute("""SELECT c.*, u.username,
        (SELECT COUNT(*) FROM reports r WHERE r.comment_id = c.id) AS report_count
        FROM comments c JOIN users u ON u.id = c.user_id
        WHERE instr(lower(c.content), lower(?)) > 0
        AND (? = 0 OR EXISTS (SELECT 1 FROM reports r WHERE r.comment_id = c.id))
        ORDER BY c.id DESC""", (query, int(reported))).fetchall()
    reports = db.execute("""SELECT r.*, u.username AS reporter FROM reports r
        JOIN users u ON u.id = r.user_id ORDER BY r.id""").fetchall()
    users = db.execute("SELECT id, username, is_admin, is_banned, is_test FROM users ORDER BY id").fetchall()
    return render_template("admin.html", comments=rows, reports=reports, users=users, query=query, reported=reported)


@app.post("/admin/users/<int:user_id>/ban")
@admin_required
def ban(user_id):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if user is None:
        abort(404)
    if user["is_admin"]:
        abort(403)
    banned = request.form.get("banned")
    if banned not in {"0", "1"}:
        abort(400)
    db.execute("UPDATE users SET is_banned = ? WHERE id = ?", (int(banned), user_id))
    db.commit()
    return redirect(url_for("admin"))


@app.post("/admin/test-data/create")
@admin_required
def create_test_data():
    db = get_db()
    credentials = []
    for _ in range(2):
        username = "practice_" + secrets.token_hex(8)
        password = secrets.token_urlsafe(18)
        cursor = db.execute("INSERT INTO users (username, password_hash, is_test) VALUES (?, ?, 1)", (username, generate_password_hash(password)))
        db.executemany("INSERT INTO comments (user_id, content, created_at) VALUES (?, ?, CURRENT_TIMESTAMP)", [(cursor.lastrowid, "[연습] 캠퍼스에서 잠시 쉬어 갑니다."), (cursor.lastrowid, "[연습] 오늘의 작은 발견을 나눕니다.")])
        credentials.append((username, password))
    db.commit()
    response = app.make_response(render_template("test_credentials.html", credentials=credentials))
    response.headers["Cache-Control"] = "no-store"
    return response


@app.post("/admin/test-data/clear")
@admin_required
def clear_test_data():
    db = get_db()
    # Remove both reports made by test accounts and reports on their comments.
    db.execute("DELETE FROM reports WHERE user_id IN (SELECT id FROM users WHERE is_test = 1) OR comment_id IN (SELECT id FROM comments WHERE user_id IN (SELECT id FROM users WHERE is_test = 1))")
    db.execute("DELETE FROM post_events WHERE user_id IN (SELECT id FROM users WHERE is_test = 1)")
    db.execute("DELETE FROM comments WHERE user_id IN (SELECT id FROM users WHERE is_test = 1)")
    db.execute("DELETE FROM users WHERE is_test = 1")
    db.commit()
    flash("연습 계정과 관련 기록을 정리했습니다.")
    return redirect(url_for("admin"))


@app.errorhandler(400)
def bad_request(_error):
    return render_template("error.html", code=400, message="요청을 확인해 주세요. 페이지를 새로고침한 뒤 다시 시도해 주세요."), 400


@app.errorhandler(403)
def forbidden(_error):
    return render_template("error.html", code=403, message="이 작업을 수행할 권한이 없습니다."), 403


@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", code=404, message="요청한 페이지를 찾을 수 없습니다."), 404


if __name__ == "__main__":
    app.run(port=5000)
