from typing import Iterable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import update, select, DECIMAL, delete
from sqlalchemy.sql.functions import sum

from database.engine import engine
from database.models import Users, Carts, Categories, Products, FinallyCarts

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


def db_get_product_by_name(product_name: str) -> Products:
    """Получаем продукт по имени"""
    query = select(Products).where(Products.product_name == product_name)
    return db_session.scalar(query)


def db_insert_or_update_finally_cart(cart_id, product_name, total_products, total_price):
    """Постоянная корзина. Вносим новую запись либо редактируем существующую, если такой продукт уже есть."""
    try:
        query = FinallyCarts(cart_id=cart_id, product_name=product_name,
                             quantity=total_products, final_price=total_price)
        db_session.add(query)
        db_session.commit()
        return True
    except IntegrityError:
        db_session.rollback()
        query = update(FinallyCarts).where(FinallyCarts.product_name == product_name) \
            .where(FinallyCarts.cart_id == cart_id).values(quantity=total_products, final_price=total_price)
        db_session.execute(query)
        db_session.commit()
        return False


def db_get_finally_price(chat_id: int) -> DECIMAL:
    """Получение общей суммы пользователя с постоянной корзины"""
    query = select(sum(FinallyCarts.final_price)).join(Carts).join(Users).where(Users.telegram == chat_id)
    return db_session.execute(query).fetchone()[0]


def db_get_finally_cart_products(chat_id: int) -> Iterable:
    """Получаем список товаров с корзины по telegram id пользователя"""
    query = select(FinallyCarts.product_name, FinallyCarts.quantity, FinallyCarts.final_price, FinallyCarts.cart_id) \
        .join(Carts).join(Users).where(Users.telegram == chat_id)
    return db_session.execute(query).fetchall()


def db_get_product_for_delete(chat_id: int) -> Iterable:
    query = select(FinallyCarts.id, FinallyCarts.product_name).join(Carts).join(Users).where(Users.telegram == chat_id)
    return db_session.execute(query).fetchall()


def db_delete_product(finally_id: int):
    """Удаление товара"""
    query = delete(FinallyCarts).where(FinallyCarts.id == finally_id)
    db_session.execute(query)
    db_session.commit()
