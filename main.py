import os
import asyncio
from dotenv import load_dotenv, find_dotenv

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start(message: Message):
    await message.answer(f'Здравствуйте, <b>{message.from_user.full_name}</b>!\n Вас приветствует бот доставки шаурмы!')


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
