import asyncio

from create_bot import dp, bot
from handlers.users import users_router

dp.include_router(users_router)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
