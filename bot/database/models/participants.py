from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from .. import Base 

class Participation(Base): #Участие
    __tablename__ = 'participants'

    id: Mapped[int] = mapped_column(primary_key=True)
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    giveaway_id: Mapped[int] = mapped_column(ForeignKey('giveaways.id'))
    
    user: Mapped['User'] = relationship('User', back_populates='participations') # пользователи
    giveaway: Mapped['Giveaway'] = relationship('Giveaway', back_populates='participants') # розыгрыши
