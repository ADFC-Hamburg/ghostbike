from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine

DB = PostgresEngine(
    config={
        "database": "ghostbikedb",
        "user": "postgres",
        "password": "postgres",
        "host": "db",
        "port": 5432,
    }
)

APP_REGISTRY = AppRegistry(apps=[
    "ghostbike.piccolo_app"])
