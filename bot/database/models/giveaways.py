from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .. import Base

class Giveaway(Base):
    __tablename__ = 'giveaways'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(String(896))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    end_date: Mapped[datetime] = mapped_column(DateTime)
    
    creator_id: Mapped[int] = mapped_column(ForeignKey('users.id')) 
    creator: Mapped['User'] = relationship('User', back_populates='giveaways') # создатель
    
    participants: Mapped[list['Participation']] = relationship('Participation', back_populates='giveaway') # Участие