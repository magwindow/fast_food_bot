import os
import asyncio
from dotenv import load_dotenv, find_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest

load_dotenv(find_dotenv())

from database.db_utils import db_register_user, db_update_user, db_create_user_cart, db_get_product_by_id, \
    db_get_user_cart, db_update_to_cart, db_get_product_by_name
from keyboards.reply_kb import share_phone_button, generate_main_menu, back_to_main_menu, back_arrow_button
from keyboards.inline_kb import generate_category_menu, show_product_by_category, generate_constructor_buttons
from utils.caption import text_for_caption

bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start(message: Message):
    await message.answer(f'Здравствуйте, <b>{message.from_user.full_name}</b>!\n Вас приветствует бот доставки шаурмы!')
    await start_register_user(message)


@dp.message(F.contact)
async def update_user_info_finish_register(message: Message):
    """Обновление данных пользователя его контактом"""
    chat_id = message.chat.id
    phone = message.contact.phone_number
    db_update_user(chat_id, phone)
    if db_create_user_cart(chat_id):
        await message.answer('Вы успешно зарегистрированы!')
    await show_main_menu(message)


@dp.message(F.text == '☑ Сделать заказ')
async def make_order(message: Message):
    """Реакция на кнопку 'Сделать заказ'"""
    chat_id = message.chat.id
    # TODO Получить id корзины пользователя
    await bot.send_message(chat_id=chat_id, text='Погнали!', reply_markup=back_to_main_menu())
    await message.answer('Выберите категорию', reply_markup=generate_category_menu())


@dp.message(F.text == 'Главное меню')
async def return_to_main_menu(message: Message):
    """Реакция на кнопку Главное меню"""
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await show_main_menu(message)


@dp.message(F.text == '⬅️ Назад')
async def return_to_category_menu(message: Message):
    """Назад к выбору продукта по категории"""
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    await make_order(message)


@dp.callback_query(F.data.regexp(r'category_[1-9]'))
async def show_product_button(call: CallbackQuery):
    """Показ всех продуктов выбранной категории"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    category_id = int(call.data.split('_')[-1])
    await bot.edit_message_text(text='Выберите продукт', chat_id=chat_id, message_id=message_id,
                                reply_markup=show_product_by_category(category_id))


@dp.callback_query(F.data == 'return_to_category')
async def return_to_category_button(call: CallbackQuery):
    """Возврат к выбору категории продукта"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await bot.edit_message_text(text='Выберите категорию', chat_id=chat_id, message_id=message_id,
                                reply_markup=generate_category_menu())


@dp.callback_query(F.data.contains('product_'))
async def show_product_detail(call: CallbackQuery):
    """Показ выбранного продукта с его информацией"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    product_id = int(call.data.split('_')[-1])
    product = db_get_product_by_id(product_id)
    await bot.delete_message(chat_id=chat_id, message_id=message_id)

    if user_cart := db_get_user_cart(chat_id):
        db_update_to_cart(price=product.price, cart_id=user_cart.id)

        text = text_for_caption(product.product_name, product.description, product.price)

        await bot.send_message(chat_id=chat_id, text='Выберете модификатор', reply_markup=back_arrow_button())
        await bot.send_photo(chat_id=chat_id, photo=FSInputFile(path=product.image), caption=text,
                             reply_markup=generate_constructor_buttons())
    else:
        await bot.send_message(chat_id=chat_id, text='К сожалению у нас нет, вашего контакта',
                               reply_markup=share_phone_button())


@dp.callback_query(F.data.regexp(r'action [+-]'))
async def constructor_change(call: CallbackQuery):
    """Логика конструктора"""
    chat_id = call.from_user.id
    message_id = call.message.message_id
    action = call.data.split()[-1]
    product_name = call.message.caption.split('\n')[0]
    user_cart = db_get_user_cart(chat_id)
    product = db_get_product_by_name(product_name)
    product_price = product.price

    match action:
        case '+':
            user_cart.total_products += 1
            product_price = product_price * user_cart.total_products
            db_update_to_cart(price=product_price, quantity=user_cart.total_products, cart_id=user_cart.id)
        case '-':
            if user_cart.total_products < 2:
                await call.answer('Меньше одного нельзя')
            else:
                user_cart.total_products -= 1
            product_price = product_price * user_cart.total_products
            db_update_to_cart(price=product_price, quantity=user_cart.total_products, cart_id=user_cart.id)

    text = text_for_caption(name=product_name, description=product.description, price=product_price)

    try:
        await bot.edit_message_media(chat_id=chat_id, message_id=message_id,
                                     media=InputMediaPhoto(media=FSInputFile(path=product.image), caption=text),
                                     reply_markup=generate_constructor_buttons(user_cart.total_products))
    except TelegramBadRequest as e:
        print(e)


async def start_register_user(message: Message):
    """Первая регистрация пользователя с проверкой на существование"""
    full_name = message.from_user.full_name
    chat_id = message.chat.id
    if db_register_user(full_name=full_name, chat_id=chat_id):
        await message.answer(f'Успешная авторизация, <b>{full_name}</b>!')
        await show_main_menu(message)
    else:
        await message.answer('Для связи с вами, нам нужен ваш контактный номер.',
                             reply_markup=share_phone_button())


async def show_main_menu(message: Message):
    """Сделать Заказ, История, Корзина, Настройки"""
    await message.answer('Выберите направление', reply_markup=generate_main_menu())


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
