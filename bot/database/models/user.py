from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime

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
    
    giveaways: Mapped[list['Giveaway']] = relationship('Giveaway', back_populates='creator') # розыгрыши 
    participations: Mapped[list['Participation']] = relationship('Participation', back_populates='user') # участия