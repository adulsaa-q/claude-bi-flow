"""Behavioral tests in disposable repositories; no Desktop, DW or real secrets."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "sql_readonly"))
from readonly_guard import validate_select


class SqlGuardTests(unittest.TestCase):
    def test_allowed_reads(self):
        for query in ["SELECT 1", "SELECT 'DELETE; BACKUP' AS [UPDATE]",
                      "WITH c AS (SELECT 1 AS n) SELECT n FROM c",
                      "SELECT 1 UNION ALL SELECT 2", "SELECT name FROM sys.views FOR JSON PATH",
                      "SELECT TOP 8 PackageName, Status FROM dbo.ETL_RunLog ORDER BY StartTime DESC",
                      "SELECT permission_name FROM fn_my_permissions(NULL, 'DATABASE')"]:
            with self.subTest(query=query):
                self.assertTrue(validate_select(query).startswith(("SELECT", "WITH")))

    def test_reject_writes_and_unparsed_input(self):
        for query in ["", "DELETE FROM x", "SELECT 1; SELECT 2", "SELECT 1 INTO x",
                      "SELECT 1\nBACKUP DATABASE x TO DISK='test.bak'",
                      "SELECT 1 DELETE FROM x", "SELECT 1\nDBCC SHRINKDATABASE(0)",
                      "SELECT 1\nWAITFOR DELAY '00:00:01'", "SELECT 1\nEXEC p",
                      "WITH c AS (SELECT 1 AS n) DELETE FROM x", "SELECT @x = 1",
                      "SELECT * FROM OPENQUERY(x, 'SELECT 1')", "SELECT * FROM [OPENQUERY](x, 'SELECT 1')",
                      "SELECT NEXT VALUE FOR dbo.sequence_name", "SELECT 1 /* unfinished"]:
            with self.subTest(query=query):
                with self.assertRaises(ValueError):
                    validate_select(query)


class SqlServerTimeoutTests(unittest.TestCase):
    """pyodbc applies Connection.timeout when cursor() is called, so it must be set first."""

    def test_both_tools_set_timeout_before_cursor(self):
        import types
        from unittest.mock import patch

        class FakeCursor:
            description = [("a",)]
            def execute(self, sql): pass
            def fetchmany(self, n): return []
            def fetchall(self): return []

        class FakeConn:
            timeout = 0
            seen = []
            def cursor(self):
                FakeConn.seen.append(self.timeout)
                return FakeCursor()
            def close(self): pass

        class FakeMCP:
            def __init__(self, name): pass
            def tool(self): return lambda fn: fn
            def run(self): pass

        fastmcp = types.ModuleType("mcp.server.fastmcp")
        fastmcp.FastMCP = FakeMCP
        pyodbc = types.ModuleType("pyodbc")
        pyodbc.connect = lambda *a, **k: FakeConn()
        modules = {"pyodbc": pyodbc, "mcp": types.ModuleType("mcp"),
                   "mcp.server": types.ModuleType("mcp.server"), "mcp.server.fastmcp": fastmcp}
        with patch.dict(sys.modules, modules):
            spec = importlib.util.spec_from_file_location("sql_server_under_test", ROOT / "scripts/sql_readonly/server.py")
            server = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(server)
            with patch.object(server, "_connection_string", return_value="fixture"):
                server.query("SELECT 1")
                server.list_tables()
        self.assertEqual(FakeConn.seen, [server.QUERY_TIMEOUT_S] * 2)
        self.assertGreater(server.QUERY_TIMEOUT_S, 0)


class GitGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="guard-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Guard Test")
        self.git("config", "user.email", "guard@example.invalid")
        self.git("config", "core.autocrlf", "false")
        shutil.copytree(ROOT / "scripts" / "git-hooks", self.root / "scripts" / "git-hooks")
        subprocess.run(["bash", "scripts/git-hooks/install.sh"], cwd=self.root, check=True, capture_output=True)
        self.git("add", "scripts")
        self.git("commit", "-qm", "Install fixture guards")

    def git(self, *args, ok=True, cwd=None):
        result = subprocess.run(["git", *args], cwd=cwd or self.root, capture_output=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        return result

    def fixture(self, name, data):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        self.git("add", "--", name)
        return p

    def test_added_and_renamed_env(self):
        self.fixture(".env", b"FAKE=fixture-only\n")
        self.assertNotEqual(self.git("commit", "-qm", "reject", ok=False).returncode, 0)
        self.git("rm", "--cached", ".env")
        self.fixture("fixture.txt", b"not a credential\n")
        self.git("commit", "-qm", "clean fixture")
        (self.root / "config").mkdir()
        self.git("mv", "fixture.txt", "config/.env")
        self.assertNotEqual(self.git("commit", "-qm", "reject rename", ok=False).returncode, 0)

    def test_staged_bom_and_unstaged_bom(self):
        for name in ["Demo.Report/definition/report.json", "Demo.Report/definition/bookmarks/a [1].json",
                     "Demo.Report/definition/pages/Thai space/visuals/v/visual.json"]:
            with self.subTest(name=name):
                p = self.fixture(name, b"\xef\xbb\xbf{}\n")
                p.write_bytes(b"{}\n")  # Worktree clean does not excuse a bad staged blob.
                self.assertNotEqual(self.git("commit", "-qm", "reject BOM", ok=False).returncode, 0)
                self.git("add", "--", name)
                p.write_bytes(b"\xef\xbb\xbf{}\n")
                self.git("commit", "-qm", "staged clean JSON")
                p.write_bytes(b"{}\n")

    def test_renamed_json_bom(self):
        self.fixture("fixture.txt", b"\xef\xbb\xbf{}\n")
        self.git("commit", "-qm", "non-report fixture")
        (self.root / "Demo.Report").mkdir()
        self.git("mv", "fixture.txt", "Demo.Report/report.json")
        self.assertNotEqual(self.git("commit", "-qm", "reject rename BOM", ok=False).returncode, 0)

    def test_credential_content_in_any_filename(self):
        # Synthetic values; keywords are assembled at runtime so this source file itself holds
        # no credential-shaped literal (this repo's own hook would flag a literal one).
        secret, P, K, W = "Zq8" + "vK2mPw7Lr", "PA" + "SS", "K" + "EY", "PW" + "D"
        blocked = {
            "notes/handover.md": f"SQL_{P}={secret}\n",
            "config/app.yaml": f"db:\n  {P.lower()}word: {secret}\n",
            "scripts/conn.ps1": f"$c = 'Server=x;Database=y;User Id=u;{P.title()}word={secret};'\n",
            "keys/id.txt": f"-----BEGIN OPENSSH PRIVATE {K}-----\nabc\n",
            "เอกสาร ไทย/api note.txt": f"API_{K}: {secret}\n",
        }
        for name, text in blocked.items():
            with self.subTest(name=name):
                self.fixture(name, text.encode("utf-8"))
                result = self.git("commit", "-qm", "reject secret", ok=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn(secret, result.stderr.decode(errors="replace"))
                self.git("rm", "-q", "--cached", "--", name)
        allowed = {
            ".env.example": f"SQL_SERVER=\nSQL_{P}=\n",
            "tests/fixture.py": f"write('SQL_{P}=fixture-only')\n",
            "server.py": f"pw = os.environ['SQL_{P}']\nconn = f'{W}={{quoted(pw)}};'\n",
            "health.ps1": f"$env:SQLCMD{P}WORD = $vals.SQL_{P}\n",
            "guard.py": f"ENV_TO{K[:1]}EN = re.compile(r'x')\n",
        }
        for name, text in allowed.items():
            self.fixture(name, text.encode("utf-8"))
        self.git("commit", "-qm", "placeholders and code references pass")
        # A clean file renamed onto a secret-bearing edit is still scanned.
        (self.root / "notes").mkdir(exist_ok=True)
        self.git("mv", "health.ps1", "notes/moved.ps1")
        (self.root / "notes/moved.ps1").write_text(f"{P}WORD={secret}\n", encoding="utf-8")
        self.git("add", "--", "notes/moved.ps1")
        self.assertNotEqual(self.git("commit", "-qm", "reject rename+edit", ok=False).returncode, 0)

    def test_linked_worktree_install(self):
        linked = Path(self.tmp.name) / "linked"
        self.git("worktree", "add", "-qb", "fixture", str(linked))
        r = subprocess.run(["bash", "scripts/git-hooks/install.sh"], cwd=linked, capture_output=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        (linked / ".env").write_bytes(b"FAKE=fixture-only\n")
        self.git("add", ".env", cwd=linked)
        self.assertNotEqual(self.git("commit", "-qm", "reject", cwd=linked, ok=False).returncode, 0)


if __name__ == "__main__":
    unittest.main()
