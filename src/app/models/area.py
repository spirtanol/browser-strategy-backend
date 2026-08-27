from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Float, String, Integer

from .base import BaseModel

class AreaModel(BaseModel):
    __tablename__ = 'areas'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False, index=False)
    empty_duration: Mapped[int] = mapped_column(Integer, nullable=False, default=0)