import os
import subprocess
from enum import StrEnum

from _pytest._code import ExceptionInfo


def assert_sqlstate_code(
    exc_info: ExceptionInfo,
    expected_sqlstate: str,
) -> None:
    sqlstate = getattr(exc_info.value.orig, "sqlstate")
    assert sqlstate == expected_sqlstate


class SQLState(StrEnum):
    CHECK_VIOLATION = "23514"
    UNIQUE_VIOLATION = "23505"
    FK_VIOLATION = "23503"
    NOT_NULL_VIOLATION = "23502"
    STRING_TOO_LONG = "22001"
    WRONG_ENUM_TYPE = "22P02"


def run_migrations(database_container) -> None:
    host = database_container.get_container_host_ip()
    port = database_container.get_exposed_port(5432)

    environment = os.environ.copy()
    environment["DATABASE__HOST"] = host
    environment["DATABASE__PORT"] = str(port)
    environment["DATABASE__USERNAME"] = database_container.username
    environment["DATABASE__PASSWORD"] = database_container.password
    environment["DATABASE__DB_NAME"] = database_container.dbname

    subprocess.run(
        ["alembic", "upgrade", "head"],
        env=environment,
        check=True,
    )
