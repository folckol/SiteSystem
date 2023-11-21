from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///results.db',pool_size=1000, max_overflow=1000)
Base = declarative_base()


class StartRaffleEventResponse(Base):
    __tablename__ = 'StartRaffleEventResponse'

    id = Column(String, primary_key=True, unique=True)
    discordId = Column(String)

    status = Column(String)
    accessedAccountsNumber = Column(Integer)
    totalAccountsNumber = Column(Integer)
    currentRaffleName = Column(String)
    endTime = Column(Integer)



Base.metadata.create_all(engine)
