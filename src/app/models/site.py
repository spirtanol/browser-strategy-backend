import enum

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON, Float, Integer
from sqlalchemy.ext.mutable import MutableDict

from .base import BaseModel
from app.defs.enums import SiteType, SiteContent


class SiteModel(BaseModel):
    __tablename__ = 'sites'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    site_type: Mapped[SiteType] = mapped_column(Integer, nullable=False, index=True, default=SiteType.STABLE)
    site_content: Mapped[SiteContent] = mapped_column(Integer, nullable=False, index=True)
    state: Mapped[dict[str, any]] = mapped_column(
        MutableDict.as_mutable(JSON),
        default=dict, 
        nullable=False,
    )