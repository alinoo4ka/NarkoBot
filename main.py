import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from datetime import datetime

API_TOKEN = '7632478806:AAElMiV06yQtnPHKgjbF_UPM0JuQiKcOlSE' # Замените на ваш токен

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

discovered_planets = 0
space_artifacts = []
planet_names = []
user_nicknames = {}
start_time = None
level_prices = [10, 30, 90, 270]
last_message = None
last_planet_search = 0


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
  global start_time, last_message
  start_time = datetime.now()
  last_message = message
  await message.answer("Привет! Я - бот, который любит исследовать космос. 🚀\n\n"
            "Начнем с создания вашего никнейма! Используйте команду /гник [никнейм]")


@dp.message_handler(commands=['космос'])
async def show_discoveries(message: types.Message):
  response = f"Найденные планеты: {', '.join(planet_names) or 'Еще не найдено ни одной планеты'}\n" # Только планеты
  await message.answer(response)


@dp.message_handler(commands=['проф', 'профиль'])
async def show_profile(message: types.Message):
  nickname = user_nicknames.get(message.from_user.id)
  response = f"{nickname}, ваш профиль:\n" if nickname else "Ваш профиль:\n"
  response += f"Всего найдено планет: {discovered_planets}\n"
  response += f"Найденные планеты: {', '.join(planet_names) or 'Еще не найдено ни одной планеты'}\n"
  response += f"Найдено космических кораблей: {space_artifacts.count('космический корабль древней цивилизации')}\n"
  response += f"Найдено осколков астероида: {space_artifacts.count('осколок астероида с редкими минералами')}\n"
  response += f"Ваш игровой уровень: {calculate_level(discovered_planets)}\n"
  response += f"Играете в бота с {start_time.strftime('%d.%m.%Y %H:%M')}"
  await message.answer(response)


@dp.message_handler(commands=['гник'])
async def set_nickname(message: types.Message):
  args = message.text.split()
  if len(args) != 2:
    await message.answer("Неправильный формат команды! Используйте /гник [никнейм]")
    return
  new_nickname = args[1]
  if new_nickname in user_nicknames.values():
    await message.answer("Этот никнейм уже занят! Попробуйте другой.")
    return
  user_nicknames[message.from_user.id] = new_nickname
  await message.answer(f"Поздравляю! Вы успешно создали себе никнейм \"{new_nickname}\"")


@dp.message_handler(commands=['уровень'])
async def show_level(message: types.Message):
    nickname = user_nicknames.get(message.from_user.id)
    current_level = calculate_level(discovered_planets)
    required_planets = level_prices[current_level - 1] if current_level < 5 else 0
    response = f"{nickname}, ваш уровень на данный момент: {current_level}\n" if nickname else f"Ваш уровень на данный момент: {current_level}\n"
    response += f"Чтобы прокачать уровень необходимо:\n"
    response += f"Планеты {discovered_planets}/{required_planets}"
    if current_level < 5:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Повысить", callback_data="upgrade_level"))
        await message.answer(response, reply_markup=keyboard)
    else:
        await message.answer(response)


@dp.callback_query_handler(lambda c: c.data == 'upgrade_level')
async def process_callback_upgrade_level(call: types.CallbackQuery):
    global discovered_planets
    current_level = calculate_level(discovered_planets)
    required_planets = level_prices[current_level - 1] if current_level < 5 else 0
    if discovered_planets >= required_planets:
        await call.message.edit_text("Ваш уровень успешно повышен!")
        discovered_planets -= required_planets
    else:
        await call.message.edit_text("Недостаточно планет!")


@dp.message_handler(regexp=r"^Искать планету$")
async def find_planet(message: types.Message):
    global last_message, last_planet_search, discovered_planets, space_artifacts, planet_names
    last_message = message
    current_time = datetime.now().timestamp()
    time_since_last_search = current_time - last_planet_search
    if time_since_last_search < 1800:
        await message.answer("Подождите, пожалуйста, перед следующим поиском должно пройти 30 минут.")
        return
    last_planet_search = current_time
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


@dp.message_handler(regexp=r"^планета (.+)$")
async def describe_planet(message: types.Message):
    planet_name = message.text.split()[1]
    planet_descriptions = {
        "Альта-42": "Планета Альта-42, покрытая лесами и озерами, славится своей богатой флорой и фауной.",
        "Бета-77": "Бета-77 - это газовый гигант, вращающийся вокруг двойной звезды.  Его атмосфера состоит из метана и аммиака.",
        "Гамма-13": "Гамма-13 - это скалистая планета с вулканической активностью,  окруженная кольцами из пыли и газа.",
        "Дельта-99": "Дельта-99 - это небольшая планета с очень низкой гравитацией,  покрытая застывшей лавой.",
        "Эпсилон-20": "Эпсилон-20 - это планета,  состоящая из чистого льда.  Она вращается вокруг красного карлика.",
        "Зи-42": "Зи-42 - это планета,  на которой обнаружены следы древней цивилизации.",
        "Эта-77": "Эта-77 - это газовый гигант,  известный своими огромными штормами.",
        "Тета-13": "Тета-13 - это планета,  на поверхности которой обнаружена вода в жидком состоянии.",
        "Йота-99": "Йота-99 - это планета,  покрытая кратерами от метеоритов."
    }
    description = planet_descriptions.get(planet_name)
    if description:
        await message.answer(description)
    else:
        await message.answer("Планета не найдена! 🕵️‍♀️")


def update_discoveries(found_message):
  global discovered_planets
  global space_artifacts
  global planet_names
  if "новую планету" in found_message:
    discovered_planets += 1
    planet_name = found_message.split("Планета: ")[1].strip()
    planet_names.append(planet_name)
  if "космический корабль" in found_message:
    space_artifacts.append("космический корабль древней цивилизации")
  if "осколок астероида" in found_message:
    space_artifacts.append("осколок астероида с редкими минералами")


def generate_planet_name():
    prefixes = ["Альта", "Бета", "Гамма", "Дельта", "Эпсилон", "Зи", "Эта", "Тета", "Йота", "Каппа"]
    suffixes = ["-42", "-77", "-13", "-99", "-20"]
    return random.choice(prefixes) + random.choice(suffixes)


def calculate_level(planets_discovered):
    if planets_discovered < 5:
        return 1
    elif planets_discovered < 10:
        return 2
    elif planets_discovered < 20:
        return 3
    else:
        return 4


async def main():
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
