"""One parsed T-SQL query. A SELECT-only database login is still required."""
import sqlglot
from sqlglot import exp
from sqlglot.tokens import TokenType

# Some statement keywords can be parsed as aliases. Quoted names and values
# are exempt; executable tokens still cannot introduce a second statement.
DENIED = frozenset("""INSERT UPDATE DELETE MERGE ALTER DROP TRUNCATE CREATE EXEC EXECUTE
GRANT REVOKE DENY INTO BACKUP RESTORE DBCC KILL SHUTDOWN RECONFIGURE USE SET DECLARE
PRINT RAISERROR THROW WAITFOR BEGIN COMMIT ROLLBACK SAVE TRANSACTION
OPENROWSET OPENQUERY OPENDATASOURCE SP_EXECUTESQL XP_CMDSHELL""".split())


def validate_select(sql: str) -> str:
    if not isinstance(sql, str) or not sql.strip():
        raise ValueError("Submit one non-empty SELECT or WITH ... SELECT query.")
    try:
        tokens = sqlglot.Dialect.get_or_raise("tsql").tokenize(sql)
        for token in tokens:
            if token.token_type not in (TokenType.STRING, TokenType.IDENTIFIER) and token.text.upper() in DENIED:
                raise ValueError("Statement/side-effect token is not allowed in a read-only query.")
        statements = [s for s in sqlglot.parse(sql, read="tsql", error_level=sqlglot.ErrorLevel.RAISE) if s is not None]
        if len(statements) != 1 or not isinstance(statements[0], (exp.Select, exp.SetOperation)):
            raise ValueError("Exactly one SELECT query is required.")
        tree = statements[0]
        for node in tree.walk():
            if isinstance(node, exp.Anonymous) and node.name.upper() in DENIED:
                raise ValueError("External execution functions are not allowed.")
            if isinstance(node, (exp.DDL, exp.DML, exp.Command, exp.Into, exp.Lock)):
                raise ValueError("Query contains a write, command or locking clause.")
            if isinstance(node, exp.Parameter):
                raise ValueError("Session variables are not supported by this read-only endpoint.")
            if isinstance(node, exp.NextValueFor):
                raise ValueError("Sequence advancement is a write, even inside SELECT.")
        return tree.sql(dialect="tsql", unsupported_level=sqlglot.ErrorLevel.RAISE)
    except (sqlglot.errors.SqlglotError, RecursionError) as exc:
        raise ValueError("Cannot validate this T-SQL query as read-only.") from exc
