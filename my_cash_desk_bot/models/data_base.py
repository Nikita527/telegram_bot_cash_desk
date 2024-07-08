import os

from dotenv import load_dotenv
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    create_engine,
    event,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

load_dotenv()

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_DB = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("DB_HOST")
DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}/{POSTGRES_DB}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    cash_balance = Column(Integer, default=0)
    non_cash_balance = Column(Integer, default=0)


class Counterparty(Base):
    __tablename__ = "counterparties"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone_or_card = Column(String)
    bank = Column(String)
    is_individual = Column(Boolean)


class CashRequest(Base):
    __tablename__ = "cash_requests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    counterparty_id = Column(Integer, ForeignKey("counterparties.id"))
    amount = Column(Integer)
    comment = Column(String)
    status = Column(Boolean)
    check_file = Column(String)
    user = relationship("User")
    counterparty = relationship("Counterparty")


class NoCashRequest(Base):
    __tablename__ = "no_cash_request"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    counterparty_id = Column(Integer, ForeignKey("counterparties.id"))
    amount = Column(Integer)
    invoice_path = Column(String)
    comment = Column(String)
    status = Column(Boolean)
    payment_slip = Column(String)
    user = relationship("User")
    counterparty = relationship("Counterparty")


def validate_cash_request(mapper, connection, target):
    if target.status and not target.check_file:
        raise IntegrityError(
            None, None, "Check is required when status is True"
        )


def validate_nocash_request(mapper, connection, target):
    if target.status and not target.payment_slip:
        raise IntegrityError(
            None, None, "Payment slip is required when status is True"
        )


event.listen(CashRequest, "before_update", validate_cash_request)
event.listen(NoCashRequest, "before_update", validate_nocash_request)


Base.metadata.create_all(bind=engine)
