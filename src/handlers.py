from aiogram import types
from typing import Union
from typing import Any
import orjson as json
import openai

from .const import DISPATCHER
from . import const


CACHE: dict[str, Any] = dict()


async def render(obj: Union[types.CallbackQuery, types.Message]) -> str:
    """
    Render a product view.
    :param obj: aiogram Message or Callback.
    :return: message text.
    """
    identifier, obj = obj.from_user.id, obj.message if isinstance(obj, types.CallbackQuery) else obj
    data = CACHE[identifier]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(text='⬅️', callback_data='prev'),
        types.InlineKeyboardButton(text=f"{data['index'] + 1}/{len(data['products'])}", callback_data='_'),
        types.InlineKeyboardButton(text='➡️', callback_data='next'),
    ]])
    product = data['products'][data['index']]
    text, params = str(product), dict(parse_mode='HTML', reply_markup=keyboard)

    if message_id := CACHE[identifier]['message_id']:
        await const.BOT.delete_message(chat_id=identifier, message_id=message_id)

    if photo := product.image_url:
        msg = await obj.answer_photo(caption=text, photo=photo, **params)
    else:
        msg = await obj.answer(text=text, **params)
    CACHE[identifier]['message_id'] = msg.message_id
    return text


@DISPATCHER.callback_query_handler(text='prev')
async def prev(obj: Union[types.CallbackQuery, types.Message]) -> str:
    """
    Render view of the previous product.
    :param obj: aiogram Message or Callback.
    :return: message text.
    """
    identifier = obj.from_user.id
    CACHE[identifier]['index'] -= 1
    if CACHE[identifier]['index'] < 0:
        CACHE[identifier]['index'] = len(CACHE[identifier]['products']) - 1
    return await render(obj)


@DISPATCHER.callback_query_handler(text='next')
async def next(obj: Union[types.CallbackQuery, types.Message]) -> str:
    """
    Render view of the next product.
    :param obj: aiogram Message or Callback.
    :return: message text.
    """
    identifier = obj.from_user.id
    CACHE[identifier]['index'] += 1
    if CACHE[identifier]['index'] > len(CACHE[identifier]['products']) - 1:
        CACHE[identifier]['index'] = 0
    return await render(obj)


async def reply(message: types.Message, response) -> None:
    """
    Reply to the user using ChatGPT message or render the product view.
    :param message: aiogram Message.
    :param response: ChatGPT's response.
    :return: None.
    """
    identifier = message.from_user.id

    if function := response['choices'][0]['message'].get('function_call', None):
        extracted = json.loads(function['arguments'])
        target = ' '.join([
            extracted.get('type', ''),
            extracted.get('name', ''),
            extracted.get('brand', ''),
            extracted.get('model', ''),
            extracted.get('details', ''),
        ]).strip()
        CACHE[identifier] = {
            'products': await const.DATA.like(target),
            'index': -1,
            'message_id': None,
        }
        if not CACHE[identifier]['products']:
            text = '￣\\_(ツ)_/￣'
            await message.answer(text=text, parse_mode='HTML')
        else:
            text = await next(message)
    else:
        text = response['choices'][0]['message']['content']
        await message.answer(text, parse_mode='HTML')
    const.OPENAI_HISTORY[identifier].append({'role': 'assistant', 'content': text})


@DISPATCHER.message_handler(content_types=['text'])
async def _(message: types.Message):
    """
    Handles any text message from the user forcing ChatGPT to reply.
    :param message: aiogram Message.
    :return:
    """
    identifier = message.from_user.id

    if identifier not in const.OPENAI_HISTORY:
        const.OPENAI_HISTORY[identifier] = [
            {
                'role': 'system',
                'content': f'''
                Ты - помощник по подбору техники в ломбарде СЕЙФ.
                Твоя задача - вести беседу с клиентом о запрашиваемом им товаре.
                Ты должен вести себя только как консультант и/или продавец, предлагать альтернативы, описывать товар
                и его характеристики и вести пользователя к тому что бы он просил тебя найти конкретный товар
                запрашивая его тип, бренд, модель, характеристики и прочие возможные детали для дальнейшего поиска
                в базе данных. Это список всех твоих товаров, не придумывай никакие другие: {const.DATA.titles}.
                '''
            }
        ]
    const.OPENAI_HISTORY[identifier].append({'role': 'user', 'content': message.text})

    response = await openai.ChatCompletion.acreate(
        model='gpt-3.5-turbo-0125',
        messages=const.OPENAI_HISTORY[identifier],
        max_tokens=500,
        temperature=0.7,
        functions=const.OPENAI_FUNCTIONS,
        function_call='auto',
    )

    await reply(message, response)
