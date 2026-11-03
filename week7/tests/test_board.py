"""Isolated integration tests. No real account or secret is used."""
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest import mock

os.environ["SECRET_KEY"] = "automated-test-secret-only"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app as board


class BoardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / "test.db")
        board.app.config.update(TESTING=True, DATABASE=self.path)
        with board.app.app_context():
            board.init_db()
            board.init_db()
        self.a = board.app.test_client()
        self.b = board.app.test_client()
        self.admin = board.app.test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def query(self, sql, args=()):
        with closing(sqlite3.connect(self.path)) as db:
            return db.execute(sql, args).fetchall()

    def token(self, client):
        with client.session_transaction() as sess:
            return sess.get("csrf_token")

    def post(self, client, path, **data):
        if not self.token(client):
            client.get("/comments")
        return client.post(path, data={"csrf_token": self.token(client), **data})

    def register(self, client, name):
        return self.post(client, "/register", username=name, password="temporary-test-password")

    def login(self, client, name, password="temporary-test-password"):
        return self.post(client, "/login", username=name, password=password)

    def promote(self, name):
        with board.app.app_context():
            board.get_db().execute("UPDATE users SET is_admin = 1 WHERE username = ?", (name,))
            board.get_db().commit()

    def test_users_csrf_and_password_hashes(self):
        self.assertEqual(self.register(self.a, "alice").status_code, 302)
        response = self.register(self.b, "alice")
        self.assertIn("이미 사용 중".encode(), response.data)
        stored = self.query("SELECT password_hash FROM users WHERE username = 'alice'")[0][0]
        self.assertNotEqual(stored, "temporary-test-password")
        self.assertTrue(board.check_password_hash(stored, "temporary-test-password"))
        self.assertIn("확인해 주세요".encode(), self.login(self.a, "alice", "wrong-password").data)
        self.assertEqual(self.login(self.a, "alice").status_code, 302)
        self.assertEqual(self.a.post("/comments", data={"content": "no token"}).status_code, 400)
        self.assertEqual(self.a.post("/comments", data={"content": "invalid", "csrf_token": "☃"}).status_code, 400)
        self.assertEqual(self.a.get("/admin").status_code, 403)

    def test_comments_reports_admin_and_cleanup(self):
        self.register(self.a, "alice"); self.login(self.a, "alice")
        self.register(self.b, "bob"); self.login(self.b, "bob")
        self.register(self.admin, "moderator"); self.promote("moderator"); self.login(self.admin, "moderator")
        self.assertEqual(self.post(self.a, "/comments", content="<script>alert(1)</script> Campus Hello").status_code, 302)
        comment_id = self.query("SELECT id FROM comments WHERE content LIKE '%Campus Hello'")[0][0]
        page = self.b.get("/comments").data
        self.assertIn(b"&lt;script&gt;", page)
        self.assertNotIn(b"<script>alert(1)</script>", page)
        self.assertEqual(self.post(self.b, f"/comments/{comment_id}/delete").status_code, 403)
        self.assertEqual(self.post(self.a, f"/comments/{comment_id}/report", reason="own").status_code, 403)
        self.assertEqual(self.post(self.b, f"/comments/{comment_id}/report", reason="needs review").status_code, 302)
        self.assertEqual(self.post(self.b, f"/comments/{comment_id}/report", reason="duplicate").status_code, 302)
        self.assertEqual(self.query("SELECT count(*) FROM reports")[0][0], 1)
        self.post(self.b, "/comments", content="Bob contribution")
        self.assertIn(b"Bob contribution", self.a.get("/comments").data)
        # An independent Python process opens the same file after writes have committed.
        env = dict(os.environ, WEEK7_DATABASE=self.path)
        command = [sys.executable, "-c", "import app; c=app.app.test_client(); r=c.get('/comments'); print('persisted' if b'Bob contribution' in r.data else 'missing')"]
        output = subprocess.check_output(command, cwd=str(Path(board.__file__).parent), env=env, text=True).strip()
        self.assertEqual(output, "persisted")
        response = self.admin.get("/admin?q=cAmPuS&reported=1")
        self.assertIn(b"Campus Hello", response.data)
        self.assertIn(b"needs review", response.data)
        self.assertNotIn(b"Bob contribution", response.data)
        self.assertEqual(self.post(self.admin, f"/comments/{comment_id}/delete").status_code, 302)
        self.assertEqual(self.query("SELECT count(*) FROM reports")[0][0], 0)
        bob_id = self.query("SELECT id FROM users WHERE username = 'bob'")[0][0]
        self.assertEqual(self.post(self.admin, f"/admin/users/{bob_id}/ban", banned="1").status_code, 302)
        self.assertEqual(self.post(self.b, "/comments", content="banned").status_code, 403)
        new_client = board.app.test_client()
        self.assertIn("제한".encode(), self.login(new_client, "bob").data)
        self.post(self.admin, f"/admin/users/{bob_id}/ban", banned="0")
        self.assertEqual(self.login(new_client, "bob").status_code, 302)
        normal_before = self.query("SELECT count(*) FROM users WHERE is_test = 0")[0][0]
        for _ in range(2):
            created = self.post(self.admin, "/admin/test-data/create")
            self.assertEqual(created.status_code, 200)
            self.assertEqual(created.headers["Cache-Control"], "no-store")
        self.assertEqual(self.query("SELECT count(*) FROM users WHERE is_test = 1")[0][0], 4)
        self.assertEqual(self.query("SELECT count(*) FROM comments WHERE content LIKE '[연습]%'")[0][0], 8)
        with closing(sqlite3.connect(self.path)) as db:
            test_id = db.execute("SELECT id FROM users WHERE is_test=1 LIMIT 1").fetchone()[0]
            test_comment = db.execute("SELECT id FROM comments WHERE user_id=?", (test_id,)).fetchone()[0]
            normal_comment = db.execute("SELECT id FROM comments WHERE content='Bob contribution'").fetchone()[0]
            alice_id = db.execute("SELECT id FROM users WHERE username='alice'").fetchone()[0]
            db.execute("INSERT INTO reports (comment_id,user_id,reason) VALUES (?,?,?)", (test_comment, alice_id, "normal on test"))
            db.execute("INSERT INTO reports (comment_id,user_id,reason) VALUES (?,?,?)", (normal_comment, test_id, "test on normal"))
            db.commit()
        self.post(self.admin, "/admin/test-data/clear")
        self.post(self.admin, "/admin/test-data/clear")
        self.assertEqual(self.query("SELECT count(*) FROM users WHERE is_test = 1")[0][0], 0)
        self.assertEqual(self.query("SELECT count(*) FROM users WHERE is_test = 0")[0][0], normal_before)
        self.assertEqual(self.query("SELECT count(*) FROM reports")[0][0], 0)
        self.assertIn(b"Bob contribution", self.a.get("/comments").data)

    def test_rate_limit_and_lengths(self):
        self.register(self.a, "writer"); self.login(self.a, "writer")
        for i in range(3):
            self.assertEqual(self.post(self.a, "/comments", content="post " + str(i)).status_code, 302)
        result = self.post(self.a, "/comments", content="fourth")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(self.query("SELECT count(*) FROM comments")[0][0], 3)
        first_id = self.query("SELECT MIN(id) FROM comments")[0][0]
        self.assertEqual(self.post(self.a, f"/comments/{first_id}/delete").status_code, 302)
        self.assertEqual(self.post(self.a, "/comments", content="after delete").status_code, 200)
        self.assertEqual(self.query("SELECT count(*) FROM comments")[0][0], 2)
        self.assertEqual(self.post(self.a, "/comments", content="x" * 301).status_code, 200)
        self.assertEqual(self.post(self.a, "/comments", content="two\nlines").status_code, 200)

    def test_migration_preserves_old_data_and_foreign_keys(self):
        legacy = str(Path(self.tmp.name) / "legacy.db")
        with closing(sqlite3.connect(legacy)) as db:
            db.executescript("""CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL);
                CREATE TABLE comments (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), content TEXT NOT NULL);
                INSERT INTO users VALUES (1, 'old', 'hash'); INSERT INTO comments VALUES (1, 1, 'old note');""")
            db.commit()
        board.app.config["DATABASE"] = legacy
        with board.app.app_context():
            board.init_db(); board.init_db()
            db = board.get_db()
            self.assertEqual(db.execute("SELECT content FROM comments WHERE id=1").fetchone()[0], "old note")
            self.assertEqual(db.execute("SELECT username FROM users WHERE id=1").fetchone()[0], "old")
            self.assertEqual(db.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            self.assertEqual(db.execute("SELECT is_test FROM users WHERE id=1").fetchone()[0], 0)

    def test_admin_commands(self):
        runner = board.app.test_cli_runner()
        self.register(self.a, "operator")
        with mock.patch.dict(os.environ, {"WEEK7_ADMIN_USERNAME": "operator"}):
            self.assertEqual(runner.invoke(args=["promote-admin"]).exit_code, 0)
        with mock.patch.dict(os.environ, {"WEEK7_ADMIN_USERNAME": "newadmin", "WEEK7_ADMIN_PASSWORD": "some-long-test-password"}):
            self.assertEqual(runner.invoke(args=["ensure-admin"]).exit_code, 0)
            self.assertEqual(runner.invoke(args=["ensure-admin"]).exit_code, 0)
        self.assertEqual(self.query("SELECT count(*) FROM users WHERE is_admin = 1")[0][0], 2)


if __name__ == "__main__":
    unittest.main()
