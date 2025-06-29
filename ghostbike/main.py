import os
from fastapi import FastAPI
from ghostbike.routes import router
from piccolo_admin.endpoints import create_admin, TableConfig

from piccolo.conf.apps import AppRegistry
from ghostbike.tables import Ghostbike,  User, Guardian, Sessions, Infrastructure, MainFault, AccidentType, LocationType, Opponent, StreetType
from piccolo_conf import DB
app = FastAPI()
app.include_router(router)

# DB-Auswahl über ENV
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

AppRegistry.apps = ["ghostbike"]

tables = [
    TableConfig(
        table_class=Ghostbike,
        visible_columns=[
            Ghostbike.death_date if hasattr(
                Ghostbike, 'death_date') else Ghostbike.date,
            Ghostbike.age,
            Ghostbike.postal_code
        ],
        visible_filters=[
            Ghostbike.death_date if hasattr(
                Ghostbike, 'death_date') else Ghostbike.date,
            Ghostbike.age,
            Ghostbike.postal_code
        ]
    ),
    TableConfig(
        table_class=User,
        visible_columns=[
            User.username,
            User.email,
            User.active,
            User.superuser
        ],
    ),
    TableConfig(
        table_class=Guardian,
        visible_columns=[
            Guardian.name,
            Guardian.email,
            Guardian.phone
        ],
    ),
]


admin = create_admin(
    tables=tables,
    auth_table=User,
    session_table=Sessions,
    site_name="Ghostbike Verwaltung",
)
app.mount("/admin/", admin)
