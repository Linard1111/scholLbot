import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
import database

# тут настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_TOKEN = 'токен свой'  # замените на ваш токен
ADMIN_ID = айди свой  # замените на ваш ID

# путь к локальным изображениям
SCHEDULE_IMAGE_SHIFT_1 = "/root/liceybot/shift_1_schedule.jpg" #на ваши пути поменяйтем 1 смена
SCHEDULE_IMAGE_SHIFT_2 = "/root/liceybot/shift_2_schedule.jpg" #на ваши пути поменяйтем 2 смена

# инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    logging.info(f"Запуск команды /start от пользователя {message.from_user.id}")
    conn = database.create_connection("bot_database.db")
    user = database.get_user(conn, message.from_user.id)

    if not user:
        username = message.from_user.username if message.from_user.username else "Не указано"
        database.add_user(conn, message.from_user.id, username)
        await message.answer("Вы успешно зарегистрированы! Зайдите в настройки чтобы посмотреть в профиль.")

        # уведомляем администратора о новом пользователе
        await bot.send_message(ADMIN_ID, f"Новый пользователь запустил бота: @{username} (ID: {message.from_user.id})")
    else:
        await message.answer("Здравствуйте!")

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Расписание Звонков", callback_data="schedule_calls"),
                types.InlineKeyboardButton("Расписание На Завтра", callback_data="schedule"))
    keyboard.add(types.InlineKeyboardButton("Электронный Дневник", url="t.me/liceyufaabot/elschool"), 
                types.InlineKeyboardButton("Мероприятия", callback_data="events"))
    keyboard.add(types.InlineKeyboardButton("Сколько Осталось До Лета", callback_data="time_until_summer"))
    keyboard.add(types.InlineKeyboardButton("Настройки", callback_data="settings"))
    keyboard.add(types.InlineKeyboardButton("FAQ", url="https://telegra.ph/FAQ-po-botu-12-02"))

    await message.answer("Приветствуем вас в боте школы 94 лицей! Выберите функцию:\n\nТакже подпишитесь на подслушано 94 лицей https://t.me/podslushano94L", reply_markup=keyboard)
    conn.close()

@dp.callback_query_handler(lambda call: call.data == "time_until_summer") #чекаем когда лето
async def time_until_summer(call: types.CallbackQuery):
    logging.info("Обработчик time_until_summer вызван")
    today = datetime.now()
    current_year = today.year

    summer_start = datetime(current_year, 6, 1)
    if today > summer_start:
        summer_start = datetime(current_year + 1, 6, 1)

    days_left = (summer_start - today).days
    await bot.send_message(call.message.chat.id, f"До Лета Осталось {days_left} Дней. \n\nНапишите /start, чтобы вернуться назад.")

@dp.callback_query_handler(lambda call: call.data == "settings")
async def settings(call: types.CallbackQuery):
    logging.info("Обработчик settings вызван")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Профиль", callback_data="profile"),
                types.InlineKeyboardButton("Сменить Класс", callback_data="set_class"))
    keyboard.add(types.InlineKeyboardButton("Люди В Вашем Классе", callback_data="class_count"),
                                            types.InlineKeyboardButton("Поддержать Проект", callback_data="support_project"))

    await bot.send_message(call.message.chat.id, "Выберите действие:", reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data == "support_project")
async def support_project(call: types.CallbackQuery):
    logging.info("Обработчик support_project вызван")
    support_message = (
        "💖 Поддержите наш проект! 💖\n\n"
        "Если вы хотите помочь, вы можете отправить средства на карту:\n"
        "🟢 Номер карты: `2200 7012 1417 2980`\n\n"
        "Также вы можете оплатить счет через Crypto bot:\n"
        "🔗 [Оплатить Через Crypto Bot](https://t.me/send?start=IVpmCRUuT0tZ)\n\n"
        "Или Через Xrocket:\n"
        "🔗 [Xrocket](https://t.me/xrocket?start=inv_SBgphwxzhKgvekn)\n\n"
        "💬 *Ваши пожертвования очень важны!\n"
        "Администратор не всегда может обслуживать бота за свои деньги, и любая помощь будет очень ценна.\n\n"
        "🔙 Напишите /start, чтобы вернуться назад!"
    )

    # экранирование спец символов
    support_message = support_message.replace("!", "\\!").replace("~", "\\~").replace("`", "\\`").replace("*", "\\*").replace("_", "\\_").replace("[", "\\[").replace("]", "\\]").replace("(", "\\(").replace(")", "\\)").replace(">", "\\>").replace("#", "\\#").replace("+", "\\+").replace("-", "\\-").replace("=", "\\=").replace("|", "\\|").replace("{", "\\{").replace("}", "\\}").replace(".", "\\.")

    # Добавляем экранирование для обратной кавычки
    support_message = support_message.replace("`2200 7012 1417 2980`", "\\`2200 7012 1417 2980\\`")

    await bot.send_message(call.message.chat.id, support_message, parse_mode='MarkdownV2')


@dp.callback_query_handler(lambda call: call.data == "schedule_calls") #расписание потом сами поменяете 
async def schedule_calls(call: types.CallbackQuery):
    logging.info("Обработчик schedule_calls вызван")
    schedule = {
        "1 Смена": [
            "1) 8:00 — 8:40 (10 минут)",
            "2) 8:50 — 9:30 (10 минут)",
            "3) 9:40 — 10:20 (10 минут)",
            "4) 10:30 — 11:10 (10 минут)",
            "5) 11:20 — 12:00 (10 минут)",
            "6) 12:10 — 12:50 (5 минут)",
            "7) 12:55 — 13:35"
        ],
        "2 Смена": [
            "1) 13:30 — 14:10 (10 минут)",
            "2) 14:20 — 15:00 (10 минут)",
            "3) 15:10 — 15:50 (10 минут)",
            "4) 16:00 — 16:40 (10 минут)",
            "5) 16:50 — 17:30 (10 минут)",
            "6) 17:40 — 18:15 (5 минут)",
            "7) 18:20 — 19:00"
        ]
    }
    response_message = ""

    for shift, lessons in schedule.items():
        response_message += f"{shift}\n"
        response_message += "\n".join(lessons) + "\n\n"

    response_message += "Напишите /start, чтобы вернуться назад."
    await bot.send_message(call.message.chat.id, response_message)

@dp.callback_query_handler(lambda call: call.data == "schedule")
async def schedule(call: types.CallbackQuery):
    logging.info("Обработчик schedule вызван")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("1 Смена", callback_data="shift_1"))
    keyboard.add(types.InlineKeyboardButton("2 Смена", callback_data="shift_2"))

    await bot.send_message(call.message.chat.id, "Выберите смену:", reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data in ["shift_1", "shift_2"]) #тут расписание которые учителя кидают выше свой путь сделаете к фото
async def handle_shift(call: types.CallbackQuery):
    logging.info("Обработчик handle_shift вызван")
    shift = "1 Смена" if call.data == "shift_1" else "2 Смена"
    schedule_image_path = SCHEDULE_IMAGE_SHIFT_1 if shift == "1 Смена" else SCHEDULE_IMAGE_SHIFT_2

    with open(schedule_image_path, 'rb') as schedule_image:
        await bot.send_photo(call.message.chat.id, schedule_image)

    await bot.send_message(call.message.chat.id, "Напишите /start, чтобы вернуться назад.")

@dp.callback_query_handler(lambda call: call.data == "events") #мп всякие
async def events(call: types.CallbackQuery):
    logging.info("Обработчик events вызван")
    conn = database.create_connection("bot_database.db")
    events_list = database.get_events(conn)

    if events_list:
        response = "\n".join([f"id {event[0]}: {event[1]} (до {event[2]})" for event in events_list])
    else:
        response = "Нет запланированных мероприятий."

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Добавить Мероприятие", callback_data='add_event')) 
    keyboard.add(types.InlineKeyboardButton("Удалить Мероприятие", callback_data='remove_event'))

    await bot.send_message(call.message.chat.id, response + "\n\nНапишите /start, чтобы вернуться назад.", reply_markup=keyboard)
    conn.close()

@dp.callback_query_handler(lambda call: call.data == 'add_event')
async def add_event_callback(call: types.CallbackQuery):
    logging.info("Обработчик add_event вызван")
    if call.from_user.id == ADMIN_ID:
        await bot.send_message(call.message.chat.id, "Введите Название Мероприятия И Количество Дней Его Хранения (например: 'Встреча 10'):")
        await dp.current_state(user=call.from_user.id).set_state('waiting_for_event_details')
    else:
        await bot.send_message(call.message.chat.id, "У вас нет прав для доступа к этой команде.")

@dp.message_handler(state='waiting_for_event_details')
async def add_event(message: types.Message):
    if message.text:
        conn = database.create_connection("bot_database.db")
        try:
            name, days = message.text.rsplit(' ', 1)
            days = int(days)
            database.add_event(conn, name, days)
            await message.answer("Мероприятие добавлено.")
        except Exception as e:
            await message.answer("Ошибка при добавлении мероприятия. Попробуйте еще раз.")
        finally:
            conn.close()
            await events(message)

@dp.callback_query_handler(lambda call: call.data == 'remove_event')
async def remove_event_callback(call: types.CallbackQuery):
    logging.info("Обработчик remove_event вызван")
    if call.from_user.id == ADMIN_ID:
        await bot.send_message(call.message.chat.id, "Введите ID Мероприятия Для Удаления:")
        await dp.current_state(user=call.from_user.id).set_state('waiting_for_event_id')
    else:
        await bot.send_message(call.message.chat.id, "У вас нет прав для доступа к этой команде.")

@dp.message_handler(state='waiting_for_event_id')
async def remove_event(message: types.Message):
    if message.text.isdigit():
        conn = database.create_connection("bot_database.db")
        try:
            event_id = int(message.text)
            database.delete_event(conn, event_id)
            await message.answer("Мероприятие удалено.")
        except Exception as e:
            await message.answer("Ошибка при удалении мероприятия. Попробуйте еще раз.")
        finally:
            conn.close()
            await events(message)

@dp.callback_query_handler(lambda call: call.data == "profile")
async def profile(call: types.CallbackQuery):
    logging.info("Обработчик profile вызван")
    conn = database.create_connection("bot_database.db")
    user = database.get_user(conn, call.from_user.id)
    if user:
        response = f"Ваш Профиль:\nИмя Пользователя: @{user[1]}\nКласс: {user[2] or 'Не Установлен'} {user[3] or ''}"
    else:
        response = "Профиль Не Найден. Используйте /start для регистрации."
    await bot.send_message(call.message.chat.id, response)
    conn.close()

@dp.callback_query_handler(lambda call: call.data == "set_class")
async def set_class(call: types.CallbackQuery):
    logging.info("Обработчик set_class вызван")
    await bot.send_message(call.message.chat.id, "Введите Ваш Класс И Букву (например: '10 A' пробел важен!):")
    await dp.current_state(user=call.from_user.id).set_state('waiting_for_class')

@dp.message_handler(state='waiting_for_class')
async def update_class(message: types.Message):
    if message.text:
        conn = database.create_connection("bot_database.db")
        try:
            parts = message.text.split()
            if len(parts) != 2:
                raise ValueError("Неверный формат. Пожалуйста, введите класс и букву в формате '10 A'.")
            class_name, class_letter = parts
            database.update_user_class(conn, message.from_user.id, class_name, class_letter)
            await message.answer("Класс Обновлён.")
        except ValueError as ve:
            await message.answer(str(ve))
        except Exception as e:
            logging.error(f"Ошибка при обновлении класса: {e}")
            await message.answer("Ошибка при обновлении класса. Попробуйте еще раз.")
        finally:
            conn.close()

        # сбрасываем состояние после успешного обновления
        await dp.current_state(user=message.from_user.id).reset_state()

        # возвращаемся в главное меню
        await start(message)
    else:
        await message.answer("Пожалуйста, введите класс и букву.")

@dp.callback_query_handler(lambda call: call.data == "class_count")
async def class_count(call: types.CallbackQuery):
    logging.info("Обработчик class_count вызван")
    conn = database.create_connection("bot_database.db")
    user = database.get_user(conn, call.from_user.id)
    if user and user[2]:
        class_name = user[2]
        class_letter = user[3]
        count = database.get_class_count(conn, class_name, class_letter)
        await bot.send_message(call.message.chat.id, f"В Вашем Классе {count} Человек(а).")
    else:
        await bot.send_message(call.message.chat.id, "Ваш Класс Не Установлен. Зайдите В Настройки Для Его Установки.") #проверочка
    conn.close()

if __name__ == '__main__':
    logging.info("Запуск бота")
    conn = database.create_connection("bot_database.db")
    database.create_table(conn)
    conn.close()

    executor.start_polling(dp, skip_updates=True)
