from fastapi import FastAPI
from ghostbike.routes import router
from piccolo_admin.endpoints import create_admin, TableConfig

from piccolo.engine.postgres import PostgresEngine
from piccolo.conf.apps import AppRegistry
from ghostbike.tables import Ghostbike,  User, Sessions

app = FastAPI()
app.include_router(router)

DB = PostgresEngine(
    config={
        "database": "ghostbikedb",
        "user": "postgres",
        "password": "postgres",
        "host": "db",
        "port": 5432,
    }
)

AppRegistry.apps = ["ghostbike"]

ghostbike_config = TableConfig(
    table_class=Ghostbike,
    visible_columns=[
        Ghostbike.death_date,
        Ghostbike.age,
        Ghostbike.postal_code
    ],
    visible_filters=[
        Ghostbike.death_date,
        Ghostbike.age,
        Ghostbike.postal_code

    ]
)

admin = create_admin(
    tables=[ghostbike_config],
    auth_table=User,
    session_table=Sessions,
    site_name="Ghostbike Verwaltung",
)
app.mount("/admin/", admin)
