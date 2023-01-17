from aiohttp import web
from db import setup_db
import asyncio
from bson import ObjectId
import re
import urllib.parse


async def shut_url_get(request):
    form_request = """<form action="/" method="POST">
    <div>
        <label for="user_url">Enter your URL:</label>
        <input name="user_url" id="user_url" value="" />
    </div>
    <div>
        <button>Send url</button>
    </div>
    </form>
    """

    return web.Response(text=form_request, content_type='text/html')


async def shut_url_post(request):
    result = await request.text()
    result = result.replace('user_url=', '')
    user_url = urllib.parse.unquote(result)
    user_url_list = user_url.split('://')
    db = request.app["db"]  # Підключення до БД
    collections = db["shortener"]
    url_record = await collections.insert_one({'url': user_url_list[1], 'protocol': user_url_list[0]})
    return web.Response(text=f"Your short url is: {str(url_record.inserted_id)}")


async def some_handler(request):
    name_url = request.match_info.get('name')
    if name_url == 'favicon.ico':
        return web.Response(status=404)
    else:
        db = request.app["db"]
        collections = db["shortener"]
        obj_url = await collections.find_one({'_id': ObjectId(name_url)})
        protocol = str(obj_url.get('protocol', 'http'))
        url = obj_url['url']
        return web.HTTPFound(protocol + '://' + url)


db = asyncio.run(setup_db())  # Чекає доки ми виконаємо підключення до БД.
app = web.Application()
app.add_routes([web.get('/', shut_url_get),
                web.get('/{name}', some_handler),
                web.post('/', shut_url_post)])
app["db"] = db

if __name__ == '__main__':
    web.run_app(app)
