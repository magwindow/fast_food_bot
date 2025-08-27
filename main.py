import os
import asyncio
from dotenv import load_dotenv, find_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

load_dotenv(find_dotenv())

from database.db_utils import db_register_user, db_update_user, db_create_user_cart
from keyboards.reply_kb import share_phone_button

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
    # await show_main_menu(message)


async def start_register_user(message: Message):
    """Первая регистрация пользователя с проверкой на существование"""
    full_name = message.from_user.full_name
    chat_id = message.chat.id
    if db_register_user(full_name=full_name, chat_id=chat_id):
        await message.answer(f'Успешная авторизация, <b>{full_name}</b>!')
    else:
        await message.answer('Для связи с вами, нам нужен ваш контактный номер.',
                             reply_markup=share_phone_button())


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
