from fastapi import APIRouter
from ghostbike.tables import Ghostbike
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

router = APIRouter()


class GhostbikeIn(BaseModel):
    death_date: date
    condition: str
    age: Optional[int]
    gender: Optional[str]
    latitude: float
    longitude: float
    postal_code: str
    street1: str
    street2: Optional[str]


class GhostbikeOut(GhostbikeIn):
    id: int


@router.post("/ghostbikes/", response_model=GhostbikeOut)
async def create_ghostbike(ghostbike: GhostbikeIn):
    obj = await Ghostbike(**ghostbike.dict()).save().returning()
    return obj.to_dict()


@router.get("/ghostbikes/", response_model=List[GhostbikeOut])
async def list_ghostbikes():
    rows = await Ghostbike.select().order_by(Ghostbike.death_date, ascending=False)
    return [r.to_dict() for r in rows]
