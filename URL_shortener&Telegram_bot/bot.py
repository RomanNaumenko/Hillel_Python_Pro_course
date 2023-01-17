import asyncio
import os

from aiogram import Bot, Dispatcher, types
from db import setup_db
# import re
from bson import ObjectId

# BOT_TOKEN = "5684708913:AAFww53fTWWfriu4h7FLZeSx-gET6d4AIbk"
BOT_TOKEN = os.environ.get('BOT_TOKEN')


async def start_handler(event: types.Message):
    await event.answer(f"Hello, {event.from_user.get_mention(as_html=True)}!", parse_mode=types.ParseMode.HTML)


async def url_handler(event: types.Message):
    db = await setup_db()
    collection = db["shortener"]
    user_url = event.text
    user_url_list = user_url.split('://')
    user_url_id = await collection.insert_one({'url': user_url_list[1], 'protocol': user_url_list[0]})
    id = user_url_id.inserted_id
    await event.answer(f"Your short url is: {id}")


async def send_url(event: types.Message):
    url = event.text
    db = await setup_db()
    collection = db["shortener"]
    obj_url = await collection.find_one({'_id': ObjectId(url)})
    protocol = str(obj_url.get('protocol', 'http'))
    url = str(obj_url['url'])
    await event.answer(f"Your url is: {protocol}://{url}")


async def main():
    bot = Bot(token=BOT_TOKEN)
    try:
        disp = Dispatcher(bot=bot)
        disp.register_message_handler(start_handler, commands={"start", "restart"})
        disp.register_message_handler(url_handler, regexp="http.+")
        disp.register_message_handler(send_url, regexp="^[0-9a-fA-F]{24}$")
        await disp.start_polling()
    finally:
        await bot.close()


asyncio.run(main())
