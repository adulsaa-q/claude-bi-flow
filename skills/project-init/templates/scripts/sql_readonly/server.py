"""SELECT-only MCP entrypoint; pair with a least-privilege SQL login.

Set SQL_ENV_PATH to the project credential file.
Install requirements.txt in the server environment before starting.
"""
import os
from readonly_guard import validate_select
import pyodbc
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sql-readonly")
QUERY_TIMEOUT_S = 60

def _load_project_env() -> dict:
    """Read KEY=VALUE pairs from the project's own .env file.

    Credentials live only in that file (already gitignored) -- never copied
    into Claude Code's own config so there is exactly one place to rotate them.
    """
    env_path = os.environ["SQL_ENV_PATH"]
    values = {}
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip()
    return values


def _connection_string() -> str:
    env = _load_project_env()
    server = env["SQL_SERVER"]
    database = env["SQL_DATABASE"]
    user = env["SQL_USER"]
    password = env["SQL_PASS"]
    def quoted(value):
        return '{' + value.replace('}', '}}') + '}'
    # Certificates are validated unless the project's .env explicitly opts out.
    trust = env.get('SQL_TRUST_SERVER_CERTIFICATE', 'no').lower()
    if trust not in ('yes', 'no'):
        raise ValueError('SQL_TRUST_SERVER_CERTIFICATE must be yes or no')
    driver = env.get('SQL_ODBC_DRIVER', 'ODBC Driver 17 for SQL Server')
    return (f'DRIVER={quoted(driver)};SERVER={quoted(server)};DATABASE={quoted(database)};'
            f'UID={quoted(user)};PWD={quoted(password)};Encrypt=yes;TrustServerCertificate={trust};')


def _assert_read_only(sql: str) -> None:
    validate_select(sql)


@mcp.tool()
def query(sql: str, max_rows: int = 500) -> str:
    """Run a SELECT query against the configured database and return a text table.

    Only SELECT / WITH-CTE statements are accepted. Everything else is rejected
    before it reaches the database.
    """
    validated = validate_select(sql)
    if not isinstance(max_rows, int) or not 1 <= max_rows <= 5000:
        raise ValueError("max_rows must be between 1 and 5000.")
    conn = pyodbc.connect(_connection_string(), timeout=15)
    try:
        conn.timeout = QUERY_TIMEOUT_S  # pyodbc applies it in cursor(); must precede it
        cur = conn.cursor()
        cur.execute(validated)
        columns = [c[0] for c in cur.description] if cur.description else []
        rows = cur.fetchmany(max_rows)
    finally:
        conn.close()

    if not columns:
        return "(no result set)"
    lines = ["\t".join(columns)]
    for row in rows:
        lines.append("\t".join("" if v is None else str(v) for v in row))
    truncated = " (truncated at max_rows)" if len(rows) == max_rows else ""
    return "\n".join(lines) + truncated


@mcp.tool()
def list_tables() -> str:
    """List tables and views in the configured database (read-only introspection)."""
    conn = pyodbc.connect(_connection_string(), timeout=15)
    try:
        conn.timeout = QUERY_TIMEOUT_S
        cur = conn.cursor()
        cur.execute(
            "SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE "
            "FROM INFORMATION_SCHEMA.TABLES ORDER BY TABLE_SCHEMA, TABLE_NAME"
        )
        rows = cur.fetchall()
    finally:
        conn.close()
    return "\n".join(f"{r.TABLE_SCHEMA}.{r.TABLE_NAME}\t{r.TABLE_TYPE}" for r in rows)


if __name__ == "__main__":
    mcp.run()
