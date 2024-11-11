import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = '7632478806:AAElMiV06yQtnPHKgjbF_UPM0JuQiKcOlSE'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

discovered_planets = 0
space_artifacts = []
planet_names = []

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    await message.answer("Привет! Я - бот, который любит исследовать космос. 🚀")

@dp.message_handler(commands=['космос'])
async def show_discoveries(message: types.Message):
    response = "Ваши открытия:\n"
    for i in range(min(len(planet_names), 10)):
        response += f"Планета {planet_names[i]}\n"
    for i in range(min(len(space_artifacts), 10)):
        response += f"{space_artifacts[i]}\n"
    if len(planet_names) > 10 or len(space_artifacts) > 10:
        response += "и еще {} предметов/планет\n".format(len(planet_names) + len(space_artifacts) - 20)
    response += f"Всего планет: {discovered_planets}"
    await message.answer(response)

@dp.message_handler(regexp=r"^Искать планету$")
async def find_planet(message: types.Message):
    global discovered_planets
    global space_artifacts
    global planet_names
    messages = [
        "Отлично! Вы обнаружили новую планету в галактике Андромеды! 🎉\nПланета: {planet_name}",
        "АХУЕТЬ! Во время сканирования космоса вы наткнулись на три новых объекта!\n+1 новая планета\nПланета: {planet_name}\n+космический корабль древней цивилизации\n+осколок астероида с редкими минералами",
        "Удача улыбнулась вам! Вы нашли планету, похожую на Землю, в созвездии Ориона! 🌎\nПланета: {planet_name}",
        "Ого! Вы обнаружили планету, вращающуюся вокруг двойной звезды! 🪐\nПланета: {planet_name}",
        "Ваши исследования принесли плоды! Вы нашли новую планету с кольцами, как у Сатурна! 🪐\nПланета: {planet_name}"
    ]
    found_message = random.choice(messages).format(planet_name=generate_planet_name())
    await message.answer(found_message)
    update_discoveries(found_message)

async def find_planet_task():
    global discovered_planets
    global space_artifacts
    global planet_names
    while True:
        messages = [
            "Отлично! Вы обнаружили новую планету в галактике Андромеды! 🎉\nПланета: {planet_name}",
            "АХУЕТЬ! Во время сканирования космоса вы наткнулись на три новых объекта!\n+1 новая планета\nПланета: {planet_name}\n+космический корабль древней цивилизации\n+осколок астероида с редкими минералами",
            "Удача улыбнулась вам! Вы нашли планету, похожую на Землю, в созвездии Ориона! 🌎\nПланета: {planet_name}",
            "Ого! Вы обнаружили планету, вращающуюся вокруг двойной звезды! 🪐\nПланета: {planet_name}",
            "Ваши исследования принесли плоды! Вы нашли новую планету с кольцами, как у Сатурна! 🪐\nПланета: {planet_name}"
        ]
        found_message = random.choice(messages).format(planet_name=generate_planet_name())
        await message.answer(found_message)
        update_discoveries(found_message)
        await asyncio.sleep(1800)

def update_discoveries(found_message):
    global discovered_planets
    global space_artifacts
    global planet_names
    if "новую планету" in found_message:
        discovered_planets += 1
        planet_names.append(generate_planet_name())
    if "космический корабль" in found_message:
        space_artifacts.append("космический корабль древней цивилизации")
    if "осколок астероида" in found_message:
        space_artifacts.append("осколок астероида с редкими минералами")

def generate_planet_name():
    prefixes = ["Альта", "Бета", "Гамма", "Дельта", "Эпсилон", "Зи", "Эта", "Тета", "Йота", "Каппа"]
    suffixes = ["-42", "-77", "-13", "-99", "-20"]
    return random.choice(prefixes) + random.choice(suffixes)

async def main():
    asyncio.create_task(find_planet_task())
    await dp.start_polling()

if __name__ == '__main__':
    executor.start(dp, main)
