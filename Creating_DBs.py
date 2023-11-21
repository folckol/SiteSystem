from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///raffles.db',pool_size=2000, max_overflow=2000)
Base = declarative_base()

# Association table between User and Raffle
user_raffle_assoc = Table('user_raffle_assoc', Base.metadata,
                          Column('user_id', String, ForeignKey('users.id')),
                          Column('raffle_id', String, ForeignKey('raffles.id'))
                          )

user_raffle_assoc1 = Table('user_raffle_assoc1', Base.metadata,
                          Column('user_id', String, ForeignKey('users.id')),
                          Column('raffle_id', String, ForeignKey('raffles.id'))
                          )

user_raffle_assoc2 = Table('user_raffle_assoc2', Base.metadata,
                          Column('accessedRaffle_id', String, ForeignKey('accessedRaffle.id')),
                          Column('raffle_id', String, ForeignKey('raffles.id'))
                          )

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True, unique=True)
    discord_id = Column(String)
    userId = Column(String)
    CaptchaKey = Column(String)

    accounts = relationship('Accounts', backref='user', cascade='all, delete-orphan')
    my_raffles = relationship('Raffle', secondary=user_raffle_assoc, backref='users')
    favourite_raffles = relationship('Raffle', secondary=user_raffle_assoc1, backref='users_favourites')


class Accounts(Base):
    __tablename__ = 'accounts'

    id = Column(String, primary_key=True, unique=True)
    name = Column(String)
    TwitterStatus = Column(String)
    TwitterAuthToken = Column(String)
    TwitterCsrf = Column(String)
    DiscordStatus = Column(String)
    DiscordToken = Column(String)
    # MetaMaskStatus = Column(String)
    MetaMaskAddress = Column(String)
    MetaMaskPrivateKey = Column(String)
    Email = Column(String)
    ProxyStatus = Column(String)
    ProxyType = Column(String)
    ProxyData = Column(String)
    user_id = Column(String, ForeignKey('users.id'))


class Raffle(Base):
    __tablename__ = 'raffles'

    id = Column(String, primary_key=True, unique=True)
    platform = Column(String)
    category = Column(String)
    profilePicture = Column(String)
    banner = Column(String)
    TotalSupply = Column(String)
    NumberOfWinners = Column(String)
    name = Column(String)
    hold = Column(String)
    subscribers = Column(String)
    deadline = Column(String)
    platformLink = Column(String)
    captcha = Column(String)
    timestamp = Column(String)
    requirements = relationship('Requirement', backref='raffle', cascade='all, delete-orphan')
    rewards = relationship('Reward', backref='raffle', cascade='all, delete-orphan')

class AccessedRaffle(Base):
    __tablename__ = 'accessedRaffle'

    id = Column(String, primary_key=True, unique=True)
    discordId = Column(String)
    usedAccounts = Column(String)
    result = Column(String)
    raffle = relationship('Raffle', secondary=user_raffle_assoc2, backref='accessedRaffles')

class StartRaffleEventResponse(Base):
    __tablename__ = 'StartRaffleEventResponse'

    id = Column(String, primary_key=True, unique=True)
    discordId = Column(String)

    status = Column(String)
    accessedAccountsNumber = Column(Integer)
    totalAccountsNumber = Column(Integer)
    currentRaffleName = Column(String)
    endTime = Column(Integer)



class Requirement(Base):
    __tablename__ = 'requirements'

    id = Column(String, primary_key=True, unique=True)
    platform = Column(String)
    action = Column(String)
    clarification = Column(String)
    raffle_id = Column(String, ForeignKey('raffles.id'))

class Reward(Base):
    __tablename__ = 'rewards'

    id = Column(String, primary_key=True, unique=True)
    name = Column(String)
    count = Column(Integer)
    symbol = Column(String)
    raffle_id = Column(String, ForeignKey('raffles.id'))


# Base.metadata.create_all(engine)
