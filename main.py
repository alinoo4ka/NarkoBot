import asyncio
import random
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta

API_TOKEN = '7865025693:AAE6RFJAgCQpUxYljnhagEca6W5lKZFKAv8' # Замените на ваш токен
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
DB_NAME = 'planet_explorer.db'

level_prices = [1, 3, 9, 270]

def init_db():
  with sqlite3.connect(DB_NAME) as conn:
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
              user_id INTEGER PRIMARY KEY,
              nickname TEXT,
              discovered_planets INTEGER DEFAULT 0,
              space_artifacts TEXT DEFAULT '',
              planet_names TEXT DEFAULT '',
              start_time TEXT,
              user_level INTEGER DEFAULT 1
            )''') # Добавлен столбец user_level
    conn.commit()

init_db()

def get_user_data(user_id):
  try:
    with sqlite3.connect(DB_NAME) as conn:
      cursor = conn.cursor()
      cursor.execute("SELECT nickname, discovered_planets, space_artifacts, planet_names, start_time, user_level FROM users WHERE user_id = ?", (user_id,))
      data = cursor.fetchone()
      if data is None:
        return None, 0, '', '', datetime.now().isoformat(), 1
      else:
        return data
  except sqlite3.Error as e:
    print(f"Ошибка при получении данных пользователя: {e}")
    return None, 0, '', '', '', 1


def update_user_data(user_id, nickname, discovered_planets, space_artifacts, planet_names, start_time, user_level):
  try:
    with sqlite3.connect(DB_NAME) as conn:
      cursor = conn.cursor()
      cursor.execute("INSERT OR REPLACE INTO users (user_id, nickname, discovered_planets, space_artifacts, planet_names, start_time, user_level) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (user_id, nickname, discovered_planets, space_artifacts, planet_names, start_time, user_level))
      conn.commit()
  except sqlite3.Error as e:
    print(f"Ошибка при обновлении данных пользователя: {e}")


async def handle_user_data_error(message):
  await message.answer("Ошибка получения данных пользователя.")


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
  user_id = message.from_user.id
  user_data = get_user_data(user_id)
  if user_data is not None:
        nickname, discovered_planets, space_artifacts, planet_names, start_time, user_level = user_data
        await message.answer(f"Добро пожаловать обратно, {nickname or 'пользователь'}! Ваш прогресс сохранен. Ваш уровень: {user_level}")
  else:
        start_time = datetime.now().isoformat()
        update_user_data(user_id, None, 0, '', '', start_time, 1)
        await message.answer("Привет! Я - бот, который любит исследовать космос. 🚀\n\nНачнем с создания вашего никнейма! Используйте команду /гник [никнейм]")    
                
@dp.message_handler(commands=['cosmo', 'космос'])
async def show_discoveries(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    if user_data:
        planet_names_list = [p.strip() for p in user_data[3].split(',') if p.strip()] if user_data[3] else []
        response = f"Найденные планеты: {(', '.join(planet_names_list) or 'Еще не найдено ни одной планеты')}"
        await message.answer(response)
    else:
        await handle_user_data_error(message)


@dp.message_handler(commands=['profile', 'проф', 'профиль'])
async def show_profile(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    if user_data:
        nickname, discovered_planets, space_artifacts, planet_names_str, start_time_str, user_level = user_data
        
        # Формируем список планет
        planet_names_list = [p.strip() for p in planet_names_str.split(',') if p.strip()]
        
        # Обрабатываем возможное отсутствие времени начала игры
        if start_time_str:
            start_time_obj = datetime.fromisoformat(start_time_str)
        else:
            start_time_obj = datetime.now()
        
        response = f"{nickname}, ваш профиль:\n" if nickname else "Ваш профиль:\n"
        response += f"Всего найдено планет: {discovered_planets}\n"
        response += f"Найденные планеты: {(', '.join(planet_names_list) or 'Еще не найдено ни одной планеты')}\n"
        response += f"Найдено космических кораблей: {space_artifacts.count('космический корабль древней цивилизации')}\n"
        response += f"Найдено осколков астероида: {space_artifacts.count('осколок астероида с редкими минералами')}\n"
        response += f"Ваш игровой уровень: {calculate_level(discovered_planets)}\n"
        response += f"Играете в бота с: {start_time_obj.strftime('%d.%m.%Y %H:%M')}"
        await message.answer(response)
    else:
        await handle_user_data_error(message)
      
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

@dp.message_handler(regexp=r'^Искать планету$')
async def find_planet(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    if user_data is None:
        await handle_user_data_error(message)
        return

    current_time = datetime.now()
    
    try:
        last_search_time = datetime.fromisoformat(str(user_data[-1]))
        time_since_last_search = current_time - last_search_time
    except (ValueError, IndexError, TypeError):
        last_search_time = current_time
        time_to_wait = timedelta(0)
    else:
        time_to_wait = timedelta(minutes=2) - time_since_last_search

    if time_to_wait > timedelta(0):
        minutes, seconds = divmod(time_to_wait.total_seconds(), 60)
        await message.answer(f"Подождите, пожалуйста, до конца ожидания осталось: {int(minutes)} минут и {int(seconds)} секунд.")
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
    update_user_discoveries(user_id, found_message, current_time.isoformat())
  
@dp.message_handler(commands=['lvl', 'уровень'])
async def show_level(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    if user_data is None:
        await handle_user_data_error(message)
        return
    discovered_planets, user_level = user_data[1], user_data[5]
    current_level = user_level
    required_planets = level_prices[current_level - 1] if current_level <= len(level_prices) else 0
    response = f"Ваш уровень на данный момент: {current_level}\n"
    response += f"Чтобы прокачать уровень необходимо:\n"
    response += f"Планеты: {discovered_planets}/{required_planets}"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if current_level <= len(level_prices):
        markup.add(KeyboardButton("Повысить"))
    await message.answer(response, reply_markup=markup)


@dp.message_handler(lambda message: message.text == "Повысить")
async def process_callback_upgrade_level(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    if user_data is None:
        await handle_user_data_error(message)
        return
    nickname, discovered_planets, space_artifacts, planet_names, start_time, user_level = user_data
    current_level = user_level
    required_planets = level_prices[current_level - 1] if current_level <= len(level_prices) else 0
    if discovered_planets >= required_planets:
        new_level = current_level + 1
        update_user_data(user_id, nickname, discovered_planets, space_artifacts, planet_names, start_time, new_level)
        await message.answer(f"Поздравляю! Вы повысили свой уровень до {new_level}!", reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer(f"Недостаточно планет для повышения уровня. Вам нужно ещё {required_planets - discovered_planets} планет", reply_markup=types.ReplyKeyboardRemove())


def update_user_discoveries(user_id, found_message, current_time):
    try:
        user_data = get_user_data(user_id)
        if user_data is None:
            return

        nickname, discovered_planets, space_artifacts_str, planet_names_str, _ = user_data
        if "новую планету" in found_message:
            discovered_planets += 1
            try:
                planet_name = found_message.split("Планета: ")[1].strip()
                planet_names_str = planet_names_str + ',' + planet_name if planet_names_str else planet_name
            except IndexError:
                print("Ошибка: Не удалось извлечь имя планеты из сообщения.")
            if "космический корабль" in found_message:
                space_artifacts_str += ",космический корабль древней цивилизации"
            if "осколок астероида" in found_message:
                space_artifacts_str += ",осколок астероида с редкими минералами"
        update_user_data(user_id, nickname, discovered_planets, space_artifacts_str, planet_names_str, current_time)
    except Exception as e:
        print(f"Ошибка при обновлении данных о находках: {e}")
      
def generate_planet_name():
    prefixes = ["Альта", "Бета", "Гамма", "Дельта", "Эпсилон", "Зи", "Эта", "Тета", "Йота", "Каппа"]
    suffixes = ["-42", "-77", "-13", "-99", "-20"]
    return random.choice(prefixes) + random.choice(suffixes)

def calculate_level(planets_discovered):
    level = 1
    for price in level_prices:
        if planets_discovered >= price:
            level += 1
        else:
            break
    return min(level, len(level_prices) + 1)
  
@dp.message_handler(commands=['гник', 'gnick'])
async def set_nickname(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Укажите никнейм после команды /гник")
        return
    nickname = args[1]
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    if user_data:
        update_user_data(user_id, nickname, user_data[1], user_data[2], user_data[3], user_data[4])
        await message.answer(f"Ваш никнейм изменен на {nickname}")
    else:
        await handle_user_data_error(message)

async def on_startup(dp):
    print('Бот запущен')

async def on_shutdown(dp):
    await bot.close()
    print('Бот остановлен')

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True)
