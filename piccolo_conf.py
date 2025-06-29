import os
from piccolo.conf.apps import AppRegistry

DB_ENGINE = os.getenv("GHOSTBIKE_DB_ENGINE", "sqlite").lower()

if DB_ENGINE == "sqlite":
    from piccolo.engine.sqlite import SQLiteEngine

    DB = SQLiteEngine(path=os.getenv(
        "GHOSTBIKE_SQLITE_PATH", "ghostbike.sqlite3"))
else:
    from piccolo.engine.postgres import PostgresEngine

    DB = PostgresEngine(
        config={
            "database": os.getenv("GHOSTBIKE_DB_NAME", "ghostbikedb"),
            "user": os.getenv("GHOSTBIKE_DB_USER", "postgres"),
            "password": os.getenv("GHOSTBIKE_DB_PASSWORD", "postgres"),
            "host": os.getenv("GHOSTBIKE_DB_HOST", "db"),
            "port": int(os.getenv("GHOSTBIKE_DB_PORT", 5432)),
        }
    )

APP_REGISTRY = AppRegistry(apps=[
    "ghostbike.piccolo_app"
])
