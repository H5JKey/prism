import os
import subprocess


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
