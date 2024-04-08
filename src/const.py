from dotenv import load_dotenv

assert load_dotenv('.env')  # keep before imports of custom modules


from aiogram import Bot, Dispatcher
from contextlib import suppress
import orjson as json
import asyncio
import openai
import os

from . import dntrade


openai.api_key = os.getenv('OPENAI_KEY')
OPENAI_HISTORY: dict[int, list[dict[str, str]]] = dict()
BOT: Bot = Bot(token=os.getenv('BOT_TOKEN'))
DISPATCHER: Dispatcher = Dispatcher(bot=BOT)
DATA: dntrade.Data = dntrade.Data()
with open('functions.json', 'r') as f:
    OPENAI_FUNCTIONS: list[dict] = json.loads(f.read())
with suppress(ImportError):
    import uvloop  # noqa
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
LOOP: asyncio.AbstractEventLoop = asyncio.new_event_loop()
