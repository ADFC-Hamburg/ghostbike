from enum import Enum
from piccolo.table import Table
from piccolo.columns import Varchar, Integer, Date, ForeignKey, Boolean, Text, BigInt, DoublePrecision, Bytea
from piccolo.columns.column_types import Serial
from piccolo_api.session_auth.tables import SessionsBase
from piccolo.apps.user.tables import BaseUser
from piccolo.columns.readable import Readable
from piccolo.columns import M2M


class StatusEnum(int, Enum):
    okay = 1
    work_needed = 2
    destroyed_or_not_there = 0


class Gender(str, Enum):
    male = "m"
    female = "f"
    non_binary = "n"


# Lookup-Tabellen
class StreetType(Table):
    id = Serial(primary_key=True)
    key = Varchar(length=2, unique=True)
    name = Varchar(length=40, unique=True)

    @classmethod
    def get_readable(cls):
        return Readable(template="%s - %s", columns=[cls.key, cls.name])


class AccidentType(Table):
    id = Serial(primary_key=True)
    key = Varchar(length=9, unique=True)
    name = Varchar(length=30, unique=True)

    @classmethod
    def get_readable(cls):
        return Readable(template="%s - %s", columns=[cls.key, cls.name])


class LocationType(Table):
    id = Serial(primary_key=True)
    key = Varchar(length=3, unique=True)
    name = Varchar(length=50, unique=True)

    @classmethod
    def get_readable(cls):
        return Readable(template="%s - %s", columns=[cls.key, cls.name])


class Opponent(Table):
    id = Serial(primary_key=True)
    key = Varchar(length=1, unique=True)
    name = Varchar(length=30, unique=True)

    @classmethod
    def get_readable(cls):
        return Readable(template="%s - %s", columns=[cls.key, cls.name])


class Infrastructure(Table):
    id = Serial(primary_key=True)
    key = Varchar(length=3, unique=True)
    name = Varchar(length=50, unique=True)

    @classmethod
    def get_readable(cls):
        return Readable(template="%s - %s", columns=[cls.key, cls.name])


class MainFault(Table):
    id = Serial(primary_key=True)
    key = Varchar(length=10, unique=True)
    name = Varchar(length=90, unique=True)

    @classmethod
    def get_readable(cls):
        return Readable(template="%s - %s", columns=[cls.key, cls.name])


class AccidentCode(Table):
    code = Integer(primary_key=True)
    name = Varchar(length=100, unique=True)
    img = Bytea(null=True, help_text="Image of the accident code")

    @classmethod
    def get_readable(cls):
        return Readable(template="%d - %s", columns=[cls.code, cls.name])


class Guardian(Table):
    id = Serial(primary_key=True)
    name = Varchar(length=100, unique=True)
    email = Varchar(length=100, null=True)
    phone = Varchar(length=20, null=True)

    @classmethod
    def get_readable(cls):
        return Readable(template="%s", columns=[cls.name])


class Ghostbike(Table):
    id = Serial(primary_key=True)

    accident_date = Date()
    death_date = Date()  # Optional, for deceased victims
    radunfall_index = Varchar(length=8)
    address = Varchar(length=200, null=True)
    postal_code = Varchar(length=6, null=True)
    location = Varchar(length=100)
    location_population = BigInt(null=True)
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
    accident_code = ForeignKey(references=AccidentCode)
    status = Integer(length=1, choices=StatusEnum, default=StatusEnum.okay)
    status_text = Varchar(length=20, null=True)
    status_checked_date = Date()
    latitude = DoublePrecision(null=True)
    longitude = DoublePrecision(null=True)
    osm_memorial_id = BigInt(
        default=-1, help_text="OpenStreetMap memorial ID, if available")

    def osm_link(self):
        """Get link to OpenStreetMap"""
        return f"http://www.openstreetmap.org/?mlat={self.latitude}&mlon={self.longitude}&zoom=15{self.id}"

    def google_link(self):
        """Get link to Google Maps"""
        return f"https://www.google.de/maps/@{self.latitude},{self.longitude},80m/data=!3m1!1e3!5m1!1e3",

    @classmethod
    def get_readable(cls):
        return Readable(template="%s - %s", columns=[cls.accident_date, cls.address])


class GuardianGhostbike(Table):
    guardian = ForeignKey(references=Guardian)
    ghostbike = ForeignKey(references=Ghostbike)


class NewspaperArticle(Table):
    id = Serial(primary_key=True)
    title = Varchar(length=200)
    ghostbike = ForeignKey(references=Ghostbike)
    medium = ForeignKey(references="NewspaperMedium")
    author = Varchar(length=100)
    url = Varchar(length=200)
    content = Text()
    date = Date()
    primary = Boolean(default=False)

    @classmethod
    def get_readable(cls):
        return Readable(template="%s - %s", columns=[cls.date, cls.title])


class NewspaperMedium(Table):
    id = Serial(primary_key=True)
    name = Varchar(length=100, unique=True)
    url = Varchar(length=200, null=True)

    @classmethod
    def get_readable(cls):
        return Readable(template="%s", columns=[cls.name])


# M2M-Beziehungen hinzufügen (nach den Klassendefinitionen)
Guardian.ghostbikes = M2M(Ghostbike)
Ghostbike.guardians = M2M(Guardian)


class Sessions(SessionsBase):
    pass


class User(BaseUser, tablename="piccolo_user"):
    pass
