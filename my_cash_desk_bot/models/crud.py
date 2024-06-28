from models.data_base import CashRequest, Counterparty, NoCashRequest, User
from sqlalchemy.orm import Session


def get_user(db: Session, telegram_id: str):
    """Получить пользователя по telegram_id."""
    return db.query(User).filter(User.telegram_id == telegram_id).first()


def get_all_users(db: Session):
    """Получить всех пользователей."""

    return db.query(User).all()


def create_user(
    db: Session,
    telegram_id: str,
    username: str,
    cash_balance: int = 0,
    non_cash_balance: int = 0,
):
    db_user = User(
        telegram_id=telegram_id,
        username=username,
        cash_balance=cash_balance,
        non_cash_balance=non_cash_balance,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_cash_balance(db: Session, telegram_id: str):
    """Показать баланс наличной кассы."""

    request_user = (
        db.query(User).filter(User.telegram_id == telegram_id).first()
    )
    if request_user:
        return request_user.cash_balance
    return "Пользователь не зарегестрирован."


def get_user_non_cash_balance(db: Session, telegram_id: str):
    """Показать баланс безналичной кассы."""

    request_user = (
        db.query(User).filter(User.telegram_id == telegram_id).first()
    )
    if request_user:
        return request_user.non_cash_balance
    return "Пользователь не зарегестрирован."


def update_user_balance(
    db: Session, user_id: int, cash_balance: int, non_cash_balance: int
):
    user = get_user(db, user_id)
    if user:
        user.cash_balance = cash_balance
        user.non_cash_balance = non_cash_balance
        db.commit()
        db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user:
        db.delete(user)
        db.commit()
    return user


def get_counterparty(db: Session, counterparty_name: str):
    return (
        db.query(Counterparty)
        .filter(Counterparty.name == counterparty_name)
        .first()
    )


def create_counterparty(
    db: Session, name: str, phone_or_card: str, bank: str, is_individual: bool
):
    db_counterparty = Counterparty(
        name=name,
        phone_or_card=phone_or_card,
        bank=bank,
        is_individual=is_individual,
    )
    db.add(db_counterparty)
    db.commit()
    db.refresh(db_counterparty)
    return db_counterparty


def update_counterparty(
    db: Session,
    counterparty_id: int,
    name: str,
    phone_or_card: str,
    bank: str,
    is_individual: bool,
):
    counterparty = get_counterparty(db, counterparty_id)
    if counterparty:
        counterparty.name = name
        counterparty.phone_or_card = phone_or_card
        counterparty.bank = bank
        counterparty.is_individual = is_individual
        db.commit()
        db.refresh(counterparty)
    return counterparty


def delete_counterparty(db: Session, counterparty_id: int):
    counterparty = get_counterparty(db, counterparty_id)
    if counterparty:
        db.delete(counterparty)
        db.commit()
    return counterparty


# CashRequest CRUD operations.


def get_cash_request(db: Session, cash_request_id: int):
    return (
        db.query(CashRequest).filter(CashRequest.id == cash_request_id).first()
    )


def get_unpaid_cash_request(db: Session):
    """Получение неоплаченных наличных заявок."""
    cash_requests = (
        db.query(CashRequest).filter(CashRequest.status.is_(False)).all()
    )
    return cash_requests


def create_cash_request(
    db: Session,
    user_id: int,
    counterparty_id: int,
    amount: int,
    comment: str,
    status: bool,
):
    db_cash_request = CashRequest(
        user_id=user_id,
        counterparty_id=counterparty_id,
        amount=amount,
        comment=comment,
        status=status,
    )
    db.add(db_cash_request)
    db.commit()
    db.refresh(db_cash_request)
    return db_cash_request


def update_cash_request_status(
    db: Session, request_id: int, status: bool, check_file: str
):
    request = get_cash_request(db, request_id)
    if request:
        request.status = status
        request.check_file = check_file
    db.commit()
    db.refresh(request)
    return request


def update_cash_request(
    db: Session, cash_request_id: int, amount: int, comment: str, status: bool
):
    cash_request = get_cash_request(db, cash_request_id)
    if cash_request:
        cash_request.amount = amount
        cash_request.comment = comment
        cash_request.status = status
        db.commit()
        db.refresh(cash_request)
    return cash_request


def delete_cash_request(db: Session, cash_request_id: int):
    cash_request = get_cash_request(db, cash_request_id)
    if cash_request:
        db.delete(cash_request)
        db.commit()
    return cash_request


# NoCashRequest CRUD operations


def get_no_cash_request(db: Session, no_cash_request_id: int):
    return (
        db.query(NoCashRequest)
        .filter(NoCashRequest.id == no_cash_request_id)
        .first()
    )


def get_unpaid_no_cash_request(db: Session):
    """Получение неоплаченных безналичных заявок."""
    no_cash_requests = (
        db.query(NoCashRequest).filter(NoCashRequest.status.is_(False)).all()
    )
    return no_cash_requests


def create_no_cash_request(
    db: Session,
    user_id: int,
    counterparty_id: int,
    amount: int,
    invoice_path: str,
    comment: str,
    status: bool,
):
    db_no_cash_request = NoCashRequest(
        user_id=user_id,
        counterparty_id=counterparty_id,
        amount=amount,
        invoice_path=invoice_path,
        comment=comment,
        status=status,
    )
    db.add(db_no_cash_request)
    db.commit()
    db.refresh(db_no_cash_request)
    return db_no_cash_request


def update_no_cash_request_status(
    db: Session, request_id: int, status: bool, payment_slip: str
):
    request = get_no_cash_request(db, request_id)
    if request:
        request.status = status
        request.payment_slip = payment_slip
    db.commit()
    db.refresh(request)
    return request


def update_no_cash_request(
    db: Session,
    no_cash_request_id: int,
    amount: int,
    invoice_path: str,
    comment: str,
    status: bool,
):
    no_cash_request = get_no_cash_request(db, no_cash_request_id)
    if no_cash_request:
        no_cash_request.amount = amount
        no_cash_request.invoice_path = invoice_path
        no_cash_request.comment = comment
        no_cash_request.status = status
        db.commit()
        db.refresh(no_cash_request)
    return no_cash_request


def delete_no_cash_request(db: Session, no_cash_request_id: int):
    no_cash_request = get_no_cash_request(db, no_cash_request_id)
    if no_cash_request:
        db.delete(no_cash_request)
        db.commit()
    return no_cash_request
