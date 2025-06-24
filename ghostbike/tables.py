from piccolo.table import Table
from piccolo.columns import Varchar, Integer, Date, Float
from enum import Enum
from piccolo.columns.choices import Choice
from piccolo_api.session_auth.tables import SessionsBase
from piccolo.apps.user.tables import BaseUser
from piccolo.columns.column_types import Serial
from piccolo.columns.readable import Readable


class ConditionEnum(str, Enum):
    okay = "okay"
    damaged = "damaged"
    destroyed = "destroyed"


class Gender(str, Enum):
    male = "m"
    female = "f"
    non_binary = "n"


class Ghostbike(Table):

    id = Serial(primary_key=True)

    death_date = Date()
    condition = Varchar(length=50, choices=ConditionEnum,
                        default=ConditionEnum.okay)
    age = Integer(null=True)
    gender = Varchar(length=1, choices=Gender)
    latitude = Float()
    longitude = Float()
    postal_code = Varchar(length=10)
    street1 = Varchar(length=100)
    street2 = Varchar(length=100, null=True)


class Sessions(SessionsBase):
    pass


class User(BaseUser, tablename="piccolo_user"):
    pass
