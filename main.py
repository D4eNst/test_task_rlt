import asyncio
import logging
import sys

import motor
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from decouple import config

TOKEN = config('TOKEN')
router = Router()

client = motor.motor_tornado.MotorClient(config('ME_CONFIG_MONGODB_URL'))
db = client.database
collection = db.sample_collection


@router.message(CommandStart())
async def first_handler(message: Message) -> None:
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


async def on_startup_wrapper(*args, **kwargs):
    async def on_startup():
        ...

    return on_startup


async def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)

    dp.startup.register(await on_startup_wrapper("args"))

    bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
