import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = '7632478806:AAElMiV06yQtnPHKgjbF_UPM0JuQiKcOlSE'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

mephedrone_total = 0
other_items = []

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    await message.answer("Привет! Я - бот, который любит искать закладки. 😉")

@dp.message_handler(commands=['закладка'])
async def show_stash(message: types.Message):
    response = "В вашей закладке:\n"
    response += f"{mephedrone_total}г мефедрона\n"

    if other_items:
        for item in other_items:
            response += f"{item}\n"

    await message.answer(response)

@dp.message_handler(regexp=r"^Искать закладку$")
async def find_stash(message: types.Message):
    global mephedrone_total
    global other_items

    messages = [
        "Отлично! ты нашел под кустом 5г мефедрона",
        "АХУЕТЬ, в тёмном переулке лежали 3 разные закладки, которые не успели спрятать\n+6г мефедрона\n+2г кокаина\n+пакетик снюса",
        "Удача улыбнулась тебе! В заброшенном здании ты обнаружил тайник с 8г мефедрона",
        "Ого! В мусорном баке лежали 3г мефедрона, завернутые в фольгу",
        "Нашел закладку! В ней 4г мефедрона и пачка сигарет"
    ]

    found_message = random.choice(messages)
    await message.answer(found_message)

    update_stash(found_message)


async def find_stash_task():
    global mephedrone_total
    global other_items

    while True:
        messages = [
            "Отлично! ты нашел под кустом 5г мефедрона",
            "АХУЕТЬ, в тёмном переулке лежали 3 разные закладки, которые не успели спрятать\n+6г мефедрона\n+2г кокаина\n+пакетик снюса",
            "Удача улыбнулась тебе! В заброшенном здании ты обнаружил тайник с 8г мефедрона",
            "Ого! В мусорном баке лежали 3г мефедрона, завернутые в фольгу",
            "Нашел закладку! В ней 4г мефедрона и пачка сигарет"
        ]

        found_message = random.choice(messages)
        await message.answer(found_message) 

        update_stash(found_message)

        await asyncio.sleep(1800)


def update_stash(found_message):
    global mephedrone_total
    global other_items

    if "мефедрона" in found_message:
        mephedrone_amount = int(found_message.split(" ")[1].replace("г", ""))
        mephedrone_total += mephedrone_amount

    if "кокаина" in found_message:
        cocaine_amount = int(found_message.split(" ")[1].replace("г", ""))
        other_items.append(f"{cocaine_amount}г кокаина")

    if "снюса" in found_message:
        other_items.append("пакетик снюса")

    if "сигарет" in found_message:
        other_items.append("пачка сигарет")


async def main():
    asyncio.create_task(find_stash_task())
    await dp.start_polling()


if __name__ == '__main__':
    executor.start(dp, main)
