from pydantic import BaseModel

from app.defs.enums import SiteContent, SiteType


class MapPlatformOut(BaseModel):
    id: int
    x: float
    y: float
    name: str
    owner_id: int
    owner_name: str


class MapSiteOut(BaseModel):
    id: int
    x: float
    y: float
    site_type: SiteType
    site_content: SiteContent


class MapAreaOut(BaseModel):
    id: int
    x: float
    y: float
    name: str


class MapFleetOut(BaseModel):
    id: int
    x: float
    y: float
    owner_id: int
    owner_name: str


class PlayerMapOut(BaseModel):
    platforms: list[MapPlatformOut]
    sites: list[MapSiteOut]
    areas: list[MapAreaOut]
    fleets: list[MapFleetOut]
