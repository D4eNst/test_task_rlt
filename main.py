import asyncio
import json
import logging
import sys
from datetime import datetime

import motor
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from decouple import config

import utils

TOKEN = config('TOKEN')
router = Router()


client = motor.motor_tornado.MotorClient(config('ME_CONFIG_MONGODB_URL'))
db = client.database
collection = db.sample_collection


@router.message(CommandStart())
async def first_handler(message: Message) -> None:
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


@router.message()
async def answer(message: Message) -> None:
    data = json.loads(message.text)
    format_str = '%Y-%m-%dT%H:%M:%S'
    dt_from = datetime.strptime(data["dt_from"], format_str)
    dt_upto = datetime.strptime(data["dt_upto"], format_str)

    group_type_format = {
        "hour": '%Y-%m-%dT%H:00:00',
        "day": '%Y-%m-%dT00:00:00',
        "month": '%Y-%m-01T00:00:00'
    }
    group_type = data["group_type"]
    format_str = group_type_format[group_type]

    formatted_dt_from_str = dt_from.strftime(format_str)
    formatted_dt_upto_str = dt_upto.strftime(format_str)

    dt_from_in_ans = datetime.strptime(formatted_dt_from_str, format_str)
    dt_upto_in_ans = datetime.strptime(formatted_dt_upto_str, format_str)

    dataset = []

    ans = {
        "dataset": dataset,
        "labels": utils.generate_time_range(dt_from_in_ans, dt_upto_in_ans, group_type)
    }

    # Транзакцию можно использовать с помощью кода
    # async with await client.start_session() as s:
    #     async with s.start_transaction():
    # В данном случае используется всего одна команда, к тому же данные никак не меняются, поэтому я её не использовал
    pipeline = utils.get_pipline(dt_from, dt_upto, format_str)
    result = await collection.aggregate(pipeline).to_list(None)

    start_date_in_answer = result[0]["_id"]

    i = 0
    while i < len(ans["labels"]) and ans["labels"][i] != start_date_in_answer:
        dataset.append(0)
        i += 1

    for item in result:
        dataset.append(item["sum"])
        i += 1

    while i < len(ans["labels"]):
        dataset.append(0)
        i += 1

    print(json.dumps(ans))
    await message.answer(json.dumps(ans))


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
        await client.close()
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
