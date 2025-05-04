from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, DeclarativeBase



engine = create_engine(
    url='sqlite:///database.db',
    echo=True
)


class Base(DeclarativeBase):
    pass


Session = sessionmaker(bind=engine)


def up():
    Base.metadata.create_all(engine)

def drop():
    Base.metadata.drop_all(engine)

def migrate():
    up()
    drop()

from .models import (
    Participation,
    User,
    Giveaway
)
