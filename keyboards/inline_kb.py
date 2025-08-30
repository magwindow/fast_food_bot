from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db_utils import db_get_all_category, db_get_products, db_get_finally_price


def generate_category_menu(chat_id: int) -> InlineKeyboardMarkup:
    """Кнопки для категорий"""
    categories = db_get_all_category()
    total_price = db_get_finally_price(chat_id)
    builder = InlineKeyboardBuilder()
    # TODO Общая сумма корзины
    builder.button(text=f'Ваша корзина ({total_price if total_price else 0} сумм)', callback_data='Ваша корзина')
    [builder.button(text=category.category_name, callback_data=f'category_{category.id}') for category in categories]
    builder.adjust(1, 2)
    return builder.as_markup()


def show_product_by_category(category_id: int) -> InlineKeyboardMarkup:
    """Кнопки продуктов"""
    products = db_get_products(category_id)
    builder = InlineKeyboardBuilder()
    [builder.button(text=product.product_name, callback_data=f'product_{product.id}') for product in products]
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text='🔙 Назад', callback_data='return_to_category'))
    return builder.as_markup()


def generate_constructor_buttons(quantity=1) -> InlineKeyboardMarkup:
    """Кнопки выбора количества продуктов"""
    builder = InlineKeyboardBuilder()
    builder.button(text='➖', callback_data='action -')
    builder.button(text=str(quantity), callback_data=str(quantity))
    builder.button(text='➕', callback_data='action +')
    builder.button(text='Положить в корзину😋', callback_data='put into cart')
    builder.adjust(3, 1)
    return builder.as_markup()
