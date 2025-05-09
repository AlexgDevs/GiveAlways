from datetime import datetime
from sqlalchemy import Boolean, ForeignKey, String, DateTime

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .. import Base



class User(Base): # Пользователь
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    joined: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    block_status: Mapped[bool] = mapped_column(default=False)

    giveaways: Mapped[list['Giveaway']] = relationship('Giveaway', back_populates='creator',  foreign_keys='Giveaway.creator_id') # розыгрыши 
    participations: Mapped[list['Participation']] = relationship('Participation', back_populates='user') # участия

    won_giveaways: Mapped[list['Giveaway']] = relationship('Giveaway', back_populates='winner', foreign_keys='Giveaway.winner_id')