from typing import Iterable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import update, select, DECIMAL

from database.engine import engine
from database.models import Users, Carts, Categories, Products

with Session(engine) as session:
    db_session = session


def db_register_user(full_name: str, chat_id: int) -> bool:
    """Первая регистрация пользователя с доступными данными"""
    try:
        # Если пользователь не существует
        query = Users(name=full_name, telegram=chat_id)
        db_session.add(query)
        db_session.commit()
        return False
    except IntegrityError:
        # Если пользователь существует
        db_session.rollback()
        return True


def db_update_user(chat_id: int, phone: str):
    """Дополняем данные пользователя телефонным номером"""
    query = update(Users).where(Users.telegram == chat_id).values(phone=phone)
    db_session.execute(query)
    db_session.commit()


def db_create_user_cart(chat_id: int):
    """Создаем временную корзину для пользователя"""
    try:
        subquery = db_session.scalar(select(Users).where(Users.telegram == chat_id))
        query = Carts(user_id=subquery.id)
        db_session.add(query)
        db_session.commit()
        return True
    except IntegrityError:
        # Если пользователь уже имеет корзину
        db_session.rollback()
    except AttributeError:
        # Если отправил контакт анонимный пользователь
        db_session.rollback()


def db_get_all_category() -> Iterable:
    """Получаем все категории"""
    query = select(Categories)
    return db_session.scalars(query)


def db_get_products(category_id: int) -> Iterable:
    """Получаем продукты категории по id категории"""
    query = select(Products).where(Products.category_id == category_id)
    return db_session.scalars(query)


def db_get_product_by_id(product_id: int) -> Products:
    """Получаем продукт по id"""
    query = select(Products).where(Products.id == product_id)
    return db_session.scalar(query)


def db_get_user_cart(chat_id: int) -> Carts:
    """Получаем id корзины по связанной таблицы Users"""
    query = select(Carts).join(Users).where(Users.telegram == chat_id)
    return db_session.scalar(query)


def db_update_to_cart(price: DECIMAL, cart_id: int, quantity=1) -> None:
    """Обновляем данные временной корзины"""
    query = update(Carts).where(Carts.id == cart_id).values(total_price=price, total_products=quantity)
    db_session.execute(query)
    db_session.commit()
