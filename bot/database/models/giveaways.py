from datetime import datetime
from typing import Optional
from sqlalchemy import JSON, Boolean, ForeignKey, String, DateTime

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .. import Base

class Giveaway(Base):
    __tablename__ = 'giveaways'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(124))
    description: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    photo: Mapped[str] = mapped_column(String(600))
    end_data: Mapped[datetime] = mapped_column(DateTime)
    requirements: Mapped[str]
    user_total: Mapped[int] = mapped_column(default=0)
    is_finished: Mapped[Boolean] = mapped_column(Boolean, default=False)

    creator_id: Mapped[int] = mapped_column(ForeignKey('users.id')) 
    creator: Mapped['User'] = relationship('User', back_populates='giveaways', foreign_keys=[creator_id]) # создатель
    participants: Mapped[list['Participation']] = relationship('Participation', back_populates='giveaway')
    
    winner_id: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id'))
    winner: Mapped[Optional['User']] = relationship( 'User',  back_populates='won_giveaways', foreign_keys=[winner_id], uselist=False)