from Parser import get_schedule_in_json, load_json
import Config
import logging
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime, date, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%d-%m-%Y %H:%M:%S')

# Добавление обработчика логов
handler = logging.FileHandler(f'logs\\{str(date.today())}.log')
#handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%d-%m-%Y %H:%M:%S'))
logging.getLogger('').addHandler(handler)

# Инициализируем бота и диспетчер
bot = Bot(token=Config.TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

list_command = """Список команд:
1. /start - Начало работы
2. /help - Помощь по командам
3. /day - Расписание на текущий день
4. /week - Расписание на теущую неделю
5. /bagreport [information] - Cообщение для администратора с информацией об ошибке
"""
weekday_names = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
short_weekday_names = {'пн':'понедельник', 'вт':'вторник', 'ср':'среда', 'чт':'четверг', 'пт':'пятница', 'сб':'суббота', 'вс':'воскресенье'}

@dp.message_handler(commands=['start', 'help', 'day', 'week', 'bagreport'])
async def ivent_command(message: types.Message):
    logging.info(f'Username: {message.from_user.username}, id: {message.from_user.id}, Имя: {message.from_user.full_name}: {message.text}')
    command = message.text.split()[0]
    if command == '/start':
        await welcome(message)
    elif command == '/help':
        await help(message)
    elif command == '/day':
        await day(message)
    elif command == '/week':
        await week(message)
    elif command == '/bagreport':
        await bagreport(message)


# Обрабатываем команду /start
async def welcome(message: types.Message):
    with open(r'img\statham.jpg', 'rb') as photo:
        await message.answer_photo(types.InputFile(photo), 'Йоу')
    await help(message)
    await replace_keyboard(message, True)


# Обрабатываем команду /help
async def help(message: types.Message):
    await message.answer(text=list_command)


# Обрабатываем команду /day
async def day(message: types.Message):
    if '⠀' in message.text:
        week = 'next_week'
        message.text = message.text.replace('⠀', '')
    else:
        week = 'current_week'

    if message.text.lower() in ['пн', 'вт', 'ср', 'чт', 'пт', 'сб']:
        day = load_json(week, short_weekday_names[message.text.lower()])
    else:
        day = load_json(week, weekday_names[date.today().weekday()])

    if day:
        for d in day[0]:
            await message.answer('-'*20+'\n'+d+'\n'+'-'*20)
    else:
        with open(r'img\today.jpg', 'rb') as photo:
            await message.answer_photo(types.InputFile(photo), 'Староста разрешает сегодня не ходить😎')


# Обрабатываем команду /week
async def week(message: types.Message):
    if '⠀' in message.text:
        week = 'next_week'
    else:
        week = 'current_week'

    full_week = load_json(week)
    for row in full_week:
        block = ''
        for item in row:
            block += item+'\n'+'-'*20+'\n'
                
        await message.answer(block)

# Обрабатываем команду /bagreport
async def bagreport(message: types.Message):
    try:
        report = message.text.split(' ', 1)[1]
        await bot.send_message(Config.ADMIN_ID, f'Баг репорт от пользователя Username: {message.from_user.username}, id: {message.from_user.id}, Имя: {message.from_user.full_name}:\n{report}')
        await message.answer('Информация передана!')
    except IndexError:
        await message.answer('Вы не ввели информацию об ошибке!\nСинтаксис данной команды:\n/bagreport [information]\n[information] - ваше сообщение об ошибке')


# Смена клавиатуры
@dp.message_handler(content_types=types.ContentType.TEXT, text=['<- Текущая неделя', 'Следующая неделя ->'])
async def replace_keyboard(message: types.Message, cur_week: bool = True):
    if message.text == 'Следующая неделя ->' or cur_week == False:
        kb = types.ReplyKeyboardMarkup(keyboard=[['<- Текущая неделя'], ['⠀Пн⠀', '⠀Вт⠀', '⠀Ср⠀', '⠀Чт⠀', '⠀Пт⠀', '⠀Сб⠀'], ['⠀Неделя⠀']], resize_keyboard=True, input_field_placeholder='Следующая неделя:')
        text = 'Выбрана следующая неделя'
    else:
        kb = types.ReplyKeyboardMarkup(keyboard=[['Следующая неделя ->'], ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'], ['Неделя', 'День']], resize_keyboard=True, input_field_placeholder='Текущая неделя:')
        text = 'Выбрана текущая неделя'

    await message.answer(text, reply_markup=kb)


dp.register_message_handler(week, content_types=types.ContentType.TEXT, regexp='(?i)^неделя$')
dp.register_message_handler(week, content_types=types.ContentType.TEXT, regexp='(?i)^⠀неделя⠀$')
dp.register_message_handler(day, content_types=types.ContentType.TEXT, regexp='(?i)^(?:пн|вт|ср|чт|пт|сб|день)$')
dp.register_message_handler(day, content_types=types.ContentType.TEXT, regexp='(?i)^⠀(?:пн|вт|ср|чт|пт|сб)⠀$')

# Обрабатываем все входящие сообщения
@dp.message_handler()
async def echo(message: types.Message):
    logging.info(f'Username: {message.from_user.username}, id: {message.from_user.id}, Имя: {message.from_user.full_name}: {message.text}')
    with open(r'img\desktop.png', 'rb') as photo:
        await message.answer_photo(types.InputFile(photo), 'Зачем ты сюда пишешь? Держи обои на рабочий стол')


if __name__ == '__main__':
    # Создание планировщика
    scheduler = AsyncIOScheduler()
    # Установка начального времени
    start_time = datetime.combine(date(2023, 4, 6), time(hour=0, minute=0))
    # Установка параметров планировщика
    scheduler.add_job(get_schedule_in_json, 'interval', hours=4, start_date=start_time)
    # Запуск планировщика
    scheduler.start()

    # Запуск бота
    executor.start_polling(dp, skip_updates=False)
