import asyncio
import multiprocessing
from datetime import datetime
from time import sleep

import requests

import starter_bot
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Update, KeyboardButton
from multiprocessing import Queue, Process


from manager.manager_app import ManagerApp
from network_file.google_doc import Google_Doc
from data_base import Data_Base
import logging
from aiogram import Bot, Dispatcher, executor, types

from tg_bot.menu import Menu

BOT_TOKEN = ManagerApp().get_json_data()["bot_token"]
admin_chat_id = "873327794"
# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize tg_bot and dispatcher
bot_telegram = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot_telegram)

process_queue_shared = multiprocessing.Manager().list()


@dp.callback_query_handler()
async def callback_handler(callback: types.CallbackQuery):
    from manager.control import Control
    print("Callback")
    try:
        print("Threads=" + str())
    except Exception as e:
        print(e)
    if callback.data == Menu.show_process_button:
        print("Show process: ")
        clients = Data_Base.get_data_by_query("select* from sessions")
        print("clients=" + str(clients))
        if len(clients) > 0:
            try:
                count = 1
                for item in clients:
                    yes = InlineKeyboardButton("Остановить", callback_data="Stop_" + str(item.get("PHONE")))
                    no = InlineKeyboardButton("Назад", callback_data="<-Назад")
                    keyboard = InlineKeyboardMarkup(row_width=1).add(yes)

                    client_info = str(count) + ") " + str(item.get("FIO")) + "\nДата записи: " + str(
                        item.get("ORDER_DATE"))
                    print("text=" + client_info)
                    if count == len(clients):
                        keyboard = InlineKeyboardMarkup(row_width=1).add(yes, no)
                    await bot_telegram.send_message(chat_id=callback.message.chat.id, text=client_info,
                                                    reply_markup=keyboard)
                    count += 1
            except Exception as e:
                print(e)
        else:
            await bot_telegram.send_message(chat_id=callback.message.chat.id,
                                            text="Нет запущенных процессов по клиентам")
    elif callback.data == Menu.help_button:
        await send_help_menu(callback.message.chat.id)
    elif callback.data == Menu.stop_all_process_button:
        if len(process_queue_shared)>0:
            yes = InlineKeyboardButton("Да", callback_data="/stopall")
            no = InlineKeyboardButton("Нет", callback_data="<-Назад")
            keyboard = InlineKeyboardMarkup().add(yes, no)
            await bot_telegram.send_message(chat_id=callback.message.chat.id, text="Вы уверены, что хотите завершить все процессы?",
                                            reply_markup=keyboard)

        else: await bot_telegram.send_message(chat_id=callback.message.chat.id, text="Нет запущенных процессов по клиентам")
    elif callback.data == "/stopall":
        await stop_process(callback)

    elif callback.data == "Назад":
        clients_button = InlineKeyboardButton(Menu.clients_button, callback_data=Menu.clients_button)
        help_button = InlineKeyboardButton(Menu.help_button, callback_data=Menu.help_button)
        keyboard = InlineKeyboardMarkup(row_width=2).add(clients_button, help_button)
        await bot_telegram.send_message(chat_id=callback.message.chat.id, text=Menu.main_menu,
                                        reply_markup=keyboard)
    elif callback.data == "<-Назад" or callback.data == Menu.clients_button:
        print("Меню клиенты")
        keyboard: InlineKeyboardMarkup = get_clients_keyboard()
        await bot_telegram.send_message(chat_id=callback.message.chat.id, text=Menu.clients_button,
                                        reply_markup=keyboard)

    elif callback.data.__contains__("Stop_"):
        try:
            phone_client = callback.data.replace("Stop_", "")
            for index, client_process in enumerate(process_queue_shared):
                if str(client_process.get("PHONE")) == str(phone_client):
                    ManagerApp.logger_main.info("Set ACTIVE=0 for " + str(phone_client))
                    print("BOT: process_queue_shared1=", process_queue_shared)
                    client_process["ACTIVE"] = 0
                    process_queue_shared[index] = client_process
                    Google_Doc().delete_row_gspread(phone_client)
                    print("BOT: client_process=", client_process)
                    # process_queue_shared.append({'PHONE': 77777777, 'ACTIVE': 1})
                    print("BOT: process_queue_shared2=", process_queue_shared)
            await bot_telegram.send_message(chat_id=callback.message.chat.id, text="Процесс остановлен")
        except Exception as e:
            print(e)

        # print("BOT: ThreadList=",bot_tg.process_queue.get())

        # await bot.send_message(callback.message.chat.id, client_info)


async def stop_process(callback):
    from manager.control import Control
    try:
        await bot_telegram.send_message(chat_id=callback.message.chat.id,
                                        text="Остановка процессов...")
        for index, client_process in enumerate(process_queue_shared):
            ManagerApp.logger_main.info("Set ACTIVE=0 for all")
            Data_Base.exec_query("update settings set monitoring_status=0")
            print("BOT: process_queue_shared1=", process_queue_shared)
            client_process["ACTIVE"] = 0
            process_queue_shared[index] = client_process
            print("BOT: client_process=", client_process)
            print("BOT: process_queue_shared2=", process_queue_shared)
            sleep(5)
        for index in range(10):
            if len(Data_Base.exec_query("select* from sessions")) > 0:
                sleep(5)
        Control().execute_bash_command("pkill -9 -f chromedriver")

        await bot_telegram.send_message(chat_id=callback.message.chat.id,
                                        text="Процессы мониторинга остановлены")
    except Exception as e:
        print(e)


# @dp.register_message_handler(on_msg :types.ContentType.all())
@dp.message_handler()
async def message_handler(message: types.Message):
    print("Вход")
    print(process_queue_shared)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == "/start":
        chatid = message.from_user.id
        date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        username = message.chat.username
        fio = message.from_user.first_name + " " + message.from_user.last_name
        language_code = message.from_user.language_code
        action_id = "0"

        if len(Data_Base.exec_query("select* from configuration where chatid=%s" % chatid))==0:
            Data_Base().exec_query(
                "insert into configuration (chatid, date, username, fio, language_code, action_id) values ('%s', '%s', '%s', '%s', '%s', '%s')" % (
                    chatid, date, username, fio, language_code, action_id))
    elif message.text == Menu.clients_button:

        keyboard = get_clients_keyboard()

        await message.answer(message.text, reply_markup=keyboard)
    elif message.text == Menu.help_button:
        await send_help_menu(message.chat.id)
    else:
        btn1 = types.KeyboardButton(Menu.clients_button)
        btn2 = types.KeyboardButton(Menu.help_button)
        keyboard.add(btn1, btn2)
        await message.answer("Главное меню", reply_markup=keyboard)


async def send_help_menu(chat_id):
    await bot_telegram.send_message(chat_id=chat_id,
                                    text="Добро пожаловать в \"Консул Вашингтон\"!\n\n" +
                         "Данный бот создан для управления мониторингом Консульского отдела ПосольстваРоссийской Федерации в Вашингтоне.\n\n" +
                         "Для добавления клиента, перейдите в меню \"Клиенты/Открыть клиентский файл\". И внесите необходимые данные клиента.\n" +
                         "*для внесения данных, требуются права доступа. Для получения прав, напишите - @as_alekseev.")

def get_clients_keyboard() -> InlineKeyboardMarkup:
    run_monitoring = InlineKeyboardButton("Включить мониторинг", callback_data="/enablemonitoring")
    process_button = InlineKeyboardButton(Menu.show_process_button, callback_data=Menu.show_process_button)
    stop_process_button = InlineKeyboardButton(Menu.stop_all_process_button, callback_data=Menu.stop_all_process_button)
    open_client_file_button = InlineKeyboardButton(
        Menu.open_client_file_button,
        url=ManagerApp().get_json_data()["document_url"],
        callback_data=Menu.open_client_file_button)
    back_button = InlineKeyboardButton("Назад", callback_data="Назад")
    if int(Data_Base.get_data_by_query("select* from settings")[0].get("MONITORING_STATUS")) == 0:
        keyboard = InlineKeyboardMarkup(row_width=1).add(run_monitoring, process_button, stop_process_button, open_client_file_button,
                                                         back_button)
    else: keyboard = InlineKeyboardMarkup(row_width=1).add(process_button, stop_process_button, open_client_file_button,
                                                     back_button)
    return keyboard


async def on_startup(_):
    await bot_telegram.send_message(admin_chat_id, "Запустился")

async def send_text(text):
    await bot_telegram.send_message(chat_id=admin_chat_id, text=text)

def send_message(chat_id, text):
    #asyncio.run(send_text(text))
    send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + text
    response = requests.get(send_text)
    return response.json()

def start_bot(process_queue):
    from manager.control import Control
    ManagerApp.logger_main.info("Start bot")
    Control().delete_sessions()
    Control().delete_temp_files_from()
    Control().enable_monitoring()
    starter_bot.process_queue_shared = process_queue
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
def send_file(path_file, chat_id):
    from manager.control import Control
    ManagerApp.logger_client.info("Send file to telegram")
    Control().execute_bash_command(
        ("curl -F document=@%s https://api.telegram.org/bot5492437032:AAHVQLoSIUClhxwKhDOFIhuj81tSjQM8MRw/sendDocument?chat_id=" + chat_id) % path_file)