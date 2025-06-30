import os
from fastapi import FastAPI
from ghostbike.routes import router
from piccolo_admin.endpoints import create_admin, TableConfig
from contextlib import asynccontextmanager
from piccolo.conf.apps import AppRegistry
from ghostbike.tables import Ghostbike,  User, Guardian, Sessions, Infrastructure, MainFault, AccidentType, LocationType, Opponent, StreetType, NewspaperArticle, NewspaperMedium
from piccolo_conf import DB
from ghostbike.db_init import initialize_default_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_default_data()
    yield
    # Shutdown (falls nötig)


app = FastAPI(lifespan=lifespan)
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
        ],
    ),
    TableConfig(
        table_class=User,
        menu_group="Einstellungen",
        visible_columns=[
            User.username,
            User.email,
            User.active,
            User.superuser
        ],
        visible_filters=[
            User.username,
            User.email,
            User.active,
            User.superuser
        ]
    ),
    TableConfig(
        table_class=Guardian,
        visible_columns=[
            Guardian.name,
            Guardian.email,
            Guardian.phone
        ],
        visible_filters=[
            Guardian.name,
            Guardian.email,
            Guardian.phone
        ]
    ),
    TableConfig(
        table_class=StreetType,
        menu_group="Lookup-Tabellen",
        link_column=StreetType.key,
        visible_columns=[
            StreetType.key,
            StreetType.name
        ],
        visible_filters=[
            StreetType.key,
            StreetType.name
        ]
    ),
    TableConfig(
        table_class=AccidentType,
        menu_group="Lookup-Tabellen",
        link_column=AccidentType.key,
        visible_columns=[AccidentType.key, AccidentType.name],
        visible_filters=[AccidentType.key, AccidentType.name]
    ),
    TableConfig(
        table_class=LocationType,
        menu_group="Lookup-Tabellen",
        visible_columns=[LocationType.key, LocationType.name],
        visible_filters=[LocationType.key, LocationType.name]
    ),
    TableConfig(
        table_class=Opponent,
        menu_group="Lookup-Tabellen",
        visible_columns=[Opponent.key, Opponent.name],
        visible_filters=[Opponent.key, Opponent.name]
    ),
    TableConfig(
        table_class=Infrastructure,
        menu_group="Lookup-Tabellen",
        visible_columns=[Infrastructure.key, Infrastructure.name],
        visible_filters=[Infrastructure.key, Infrastructure.name]
    ),
    TableConfig(
        table_class=MainFault,
        menu_group="Lookup-Tabellen",
        visible_columns=[MainFault.key, MainFault.name],
        visible_filters=[MainFault.key, MainFault.name]
    ),
    TableConfig(
        # Assuming you renamed PressRelease to NewspaperArticle
        table_class=NewspaperArticle,
        visible_columns=[
            NewspaperArticle.title,
            NewspaperArticle.medium,
            NewspaperArticle.date,
        ],
        visible_filters=[
            NewspaperArticle.title,
            NewspaperArticle.medium,
            NewspaperArticle.date,
        ]
    ),
    TableConfig(
        table_class=NewspaperMedium,
        menu_group="Lookup-Tabellen",
        visible_columns=[NewspaperMedium.name],
        visible_filters=[NewspaperMedium.name]
    ),
]


admin = create_admin(
    tables=tables,
    auth_table=User,
    session_table=Sessions,
    site_name="Ghostbike Verwaltung",
)
app.mount("/admin/", admin)
