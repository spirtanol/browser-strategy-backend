from .base import BaseModel

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON, ForeignKey
from sqlalchemy.ext.mutable import MutableDict


class ShipModel(BaseModel):
    __tablename__ = 'ships'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete='RESTRICT', onupdate='NO ACTION'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, index=False)
    state: Mapped[dict[str, any]] = mapped_column(
        MutableDict.as_mutable(JSON),
        default=dict, 
        nullable=False,
    )