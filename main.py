import asyncio

from aiogram import Bot,Dispatcher,F
from aiogram.types import Message
from openai import AsyncOpenAI

from config import telegram_token, allwd, openai_key, model_engine

bot = Bot(token=telegram_token)

dp = Dispatcher()

__temp__ = {0: []}


@dp.message(F.text == "/clear")
async def command_clear(message: Message):
    uid = message.from_user.id
    text = message.text
    if uid in allwd:
        await message.answer(f"История диалога с ботом успешно очищена!")
        if __temp__.__contains__(uid): __temp__[uid] = [];
    else:
        await message.answer(f"У вас нет доступа. Вот ваш айди: {uid}")


@dp.message()
async def message(message: Message):
    uid = message.from_user.id
    text = message.text
    if uid in allwd:
        if len(__temp__[uid]) > 10: __temp__[uid].pop(0)
        await message.answer(f"Отправили запрос в чатгпт... Сейчас будет!")
        client = AsyncOpenAI(api_key=openai_key)
        if not __temp__.__contains__(uid): __temp__[uid] = [];
        __temp__[uid].append({"role": "user", "content": text})
        response = await client.chat.completions.create(
            model=model_engine,
            messages=__temp__[uid]
        )
        __temp__[uid].append({"role": "assistant", "content": response.choices[0].message.content})
        content = response.choices[0].message.content
        if len(content) < 4096:
            await message.answer(content)
        else:
            messages = []
            while len(content) < 4096:
                messages.append(content[:4096])
                content = content[4095:]
            async for m in messages:
                await message.answer(m)
            await message.answer(content)
    else:
        await message.answer(f"У вас нет доступа. Вот ваш айди: {uid}")


async def run():
    await dp.start_polling(bot)

asyncio.run(run())