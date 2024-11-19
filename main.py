import asyncio
import random
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from datetime import datetime

API_TOKEN = '7865025693:AAE6RFJAgCQpUxYljnhagEca6W5lKZFKAv8'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
DB_NAME = 'planet_explorer.db'

def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, nickname TEXT, discovered_planets INTEGER DEFAULT 0, space_artifacts TEXT DEFAULT '', planet_names TEXT DEFAULT '', start_time TEXT)''')
  conn.commit()
  conn.close()
init_db()

def get_user_data(user_id):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("SELECT nickname, discovered_planets, space_artifacts, planet_names, start_time FROM users WHERE user_id = ?", (user_id,))
  data = cursor.fetchone()
  conn.close()
  return data

def update_user_data(user_id, nickname, discovered_planets, space_artifacts, planet_names, start_time):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("INSERT OR REPLACE INTO users (user_id, nickname, discovered_planets, space_artifacts, planet_names, start_time) VALUES (?, ?, ?, ?, ?, ?)",
          (user_id, nickname, discovered_planets, space_artifacts, planet_names, start_time))
  conn.commit()
  conn.close()

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
  user_id = message.from_user.id
  start_time = datetime.now().isoformat()
  update_user_data(user_id, None, 0, '', '', start_time)
  await message.answer("Привет! Я - бот, который любит исследовать космос. 🚀\n\nНачнем с создания вашего никнейма! Используйте команду /гник [никнейм]")

@dp.message_handler(commands=['cosmo', 'космос'])
async def show_discoveries(message: types.Message):
  user_id = message.from_user.id
  user_data = get_user_data(user_id)
  if user_data:
    planet_names_list = [p.strip() for p in user_data[3].split(',') if p.strip()] if user_data[3] else []
    response = f"Найденные планеты:\n{('\n'.join(planet_names_list) or 'Еще не найдено ни одной планеты')}"
    await message.answer(response)
  else:
    await message.answer("Ошибка получения данных пользователя.")

@dp.message_handler(commands=['profile', 'проф', 'профиль'])
async def show_profile(message: types.Message):
  user_id = message.from_user.id
  user_data = get_user_data(user_id)
  if user_data:
    nickname, discovered_planets, space_artifacts, planet_names_str, start_time_str = user_data
    planet_names_list = [p.strip() for p in planet_names_str.split(',') if p.strip()] if planet_names_str else []
    start_time_obj = datetime.fromisoformat(start_time_str)
    response = f"{nickname}, ваш профиль:\n" if nickname else "Ваш профиль:\n"
    response += f"Всего найдено планет: {discovered_planets}\n"
    response += f"Найденные планеты:\n{('\n'.join(planet_names_list) or 'Еще не найдено ни одной планеты')}\n"
    response += f"Найдено космических кораблей: {space_artifacts.count('космический корабль древней цивилизации')}\n"
    response += f"Найдено осколков астероида: {space_artifacts.count('осколок астероида с редкими минералами')}\n"
    response += f"Ваш игровой уровень: {calculate_level(discovered_planets)}\n"
    response += f"Играете в бота с: {start_time_obj.strftime('%d.%m.%Y %H:%M')}"
    await message.answer(response)
  else:
    await message.answer("Ошибка получения данных пользователя.")

@dp.message_handler(commands=['planet', 'планета'])
async def describe_planet(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Укажите название планеты после команды /планета")
        return
    planet_name = args[1]
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

@dp.message_handler(regexp=r"^Искать планету$")
async def find_planet(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    current_time = datetime.now().timestamp()
    if user_data:
        last_planet_search_time = datetime.fromisoformat(user_data[-1]).timestamp()
        time_since_last_search = current_time - last_planet_search_time
    if time_since_last_search < 1800:
      await message.answer("Подождите, пожалуйста, перед следующим поиском должно пройти 30 минут.")
      return
      messages = [
        "Отлично! Вы обнаружили новую планету в галактике Андромеды! 🎉\nПланета: {planet_name}",
        "АХУЕТЬ! Во время сканирования космоса вы наткнулись на три новых объекта!\n+1 новая планета\nПланета: {planet_name}\n+космический корабль древней цивилизации\n+осколок астероида с редкими минералами",
        "Удача улыбнулась вам! Вы нашли планету, похожую на Землю, в созвездии Ориона! 🌎\nПланета: {planet_name}",
        "Ого! Вы обнаружили планету, вращающуюся вокруг двойной звезды! 🪐\nПланета: {planet_name}",
        "Ваши исследования принесли плоды! Вы нашли новую планету с кольцами, как у Сатурна! 🪐\nПланета: {planet_name}"
      ]
      found_message = random.choice(messages).format(planet_name=generate_planet_name())
      await message.answer(found_message)
      update_user_discoveries(user_id, found_message)
    else:
      await message.answer("Ошибка получения данных пользователя.")

@dp.message_handler(commands=['lvl', 'уровень'])
async def show_level(message: types.Message):
  user_id = message.from_user.id
  user_data = get_user_data(user_id)
  if user_data:
    discovered_planets = user_data[1]
    current_level = calculate_level(discovered_planets)
    required_planets = level_prices[current_level - 1] if current_level < 5 else 0
    response = f"Ваш уровень на данный момент: {current_level}\n"
    response += f"Чтобы прокачать уровень необходимо:\n"
    response += f"Планеты: {discovered_planets}/{required_planets}"
    if current_level < 5:
      await message.answer(response, reply_markup=types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="Повысить")]]))
    else:
      await message.answer(response)
  else:
    await message.answer("Ошибка получения данных пользователя.")
      

@dp.message_handler(lambda message: message.text == "Повысить")
async def process_callback_upgrade_level(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    if user_data:
        discovered_planets = user_data[1]
        current_level = calculate_level(discovered_planets)
        required_planets = level_prices[current_level - 1] if current_level < 5 else 0
    if discovered_planets >= required_planets:
        await message.answer("Ваш уровень успешно повышен!")
        update_user_data(user_id, *user_data[:1], discovered_planets - required_planets, *user_data[3:])
    else:
        await message.answer("Недостаточно планет!")
  else:
await message.answer("Ошибка получения данных пользователя.")

def update_user_discoveries(user_id, found_message):
    user_data = get_user_data(user_id)
    if user_data:
        discovered_planets, space_artifacts_str, planet_names_str = user_data[1:4]
    if "новую планету" in found_message:
        discovered_planets += 1
      try:
        planet_name = found_message.split("Планета: ")[1].strip()
        planet_names_str += ',' + planet_name if planet_names_str else planet_name
      except IndexError:
        print("Ошибка: Не удалось извлечь имя планеты из сообщения.")
        if "космический корабль" in found_message:
            space_artifacts_str += ",космический корабль древней цивилизации"
        if "осколок астероида" in found_message:
            space_artifacts_str += ",осколок астероида с редкими минералами"
          update_user_data(user_id, *user_data[:1], discovered_planets, space_artifacts_str, planet_names_str, user_data[-1])

def generate_planet_name():
    prefixes = ["Альта", "Бета", "Гамма", "Дельта", "Эпсилон", "Зи", "Эта", "Тета", "Йота", "Каппа"]
    suffixes = ["-42", "-77", "-13", "-99", "-20"]
    return random.choice(prefixes) + random.choice(suffixes)

def calculate_level(planets_discovered):
    level_prices = [10, 30, 90, 270]
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
