from enum import Enum
from piccolo.table import Table
from piccolo.columns import Varchar, Integer, Date, Float, ForeignKey, Boolean
from piccolo.columns.column_types import Serial
from piccolo_api.session_auth.tables import SessionsBase
from piccolo.apps.user.tables import BaseUser
from piccolo.columns.readable import Readable


class ConditionEnum(str, Enum):
    okay = "okay"
    damaged = "damaged"
    destroyed = "destroyed"


class Gender(str, Enum):
    male = "m"
    female = "f"
    non_binary = "n"


# Lookup-Tabellen
class StreetType(Table):
    id = Serial(primary_key=True)
    key = Varchar(length=2, unique=True)
    name = Varchar(length=20, unique=True)


class AccidentType(Table):
    id = Serial(primary_key=True)
    key = Varchar(length=9, unique=True)
    name = Varchar(length=30, unique=True)


class LocationType(Table):
    id = Serial(primary_key=True)
    key = Varchar(length=1, unique=True)
    name = Varchar(length=20, unique=True)


class Opponent(Table):
    id = Serial(primary_key=True)
    key = Varchar(length=1, unique=True)
    name = Varchar(length=20, unique=True)


class Infrastructure(Table):
    id = Serial(primary_key=True)
    key = Varchar(length=3, unique=True)
    name = Varchar(length=20, unique=True)


class MainFault(Table):
    id = Serial(primary_key=True)
    key = Varchar(length=1, unique=True)
    name = Varchar(length=20, unique=True)


class Guardian(Table):
    id = Serial(primary_key=True)
    name = Varchar(length=100, unique=True)
    email = Varchar(length=100, null=True)
    phone = Varchar(length=20, null=True)


class Ghostbike(Table):
    id = Serial(primary_key=True)

    accident_date = Date()
    death_date = Date()  # Optional, for deceased victims
    location = Varchar(length=100)
    street_type = ForeignKey(references=StreetType)
    accident_type = ForeignKey(references=AccidentType)
    location_type = ForeignKey(references=LocationType)
    comment = Varchar(length=500, null=True)
    gender = Varchar(length=1, choices=Gender)
    age = Integer(null=True)
    pedelec = Boolean(null=True)
    opponent = ForeignKey(references=Opponent)
    infrastructure = ForeignKey(references=Infrastructure)
    main_fault = ForeignKey(references=MainFault)
    key = Varchar(length=50, null=True)
    population = Integer(null=True)
    postal_code = Varchar(length=10, null=True)
    state = Varchar(length=50, null=True)
    ghostbike_code = Varchar(length=20, null=True)
    status = Varchar(length=20, null=True)
    guardian = ForeignKey(references=Guardian)
    latitude = Float(null=True)
    longitude = Float(null=True)
    address = Varchar(length=200, null=True)
    osm_memorial_id = Integer(null=True)

    def osm_link(self):
        """Get link to OpenStreetMap"""
        return f"http://www.openstreetmap.org/?mlat={self.latitude}&mlon={self.longitude}&zoom=15{self.id}"

    def google_link(self):
        """Get link to Google Maps"""
        return f"https://www.google.de/maps/@{self.latitude},{self.longitude},80m/data=!3m1!1e3!5m1!1e3",


class Sessions(SessionsBase):
    pass


class User(BaseUser, tablename="piccolo_user"):
    pass
