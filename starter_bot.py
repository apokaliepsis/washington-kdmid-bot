import asyncio
import multiprocessing
from datetime import datetime
from time import sleep
import requests

import main
import starter_bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Update, KeyboardButton

from manager.manager_app import ManagerApp
from network_file.google_doc import Google_Doc
from data_base import Data_Base
import logging
from aiogram import Bot, Dispatcher, executor, types
from tg_bot.menu import Menu


def get_token_bot():
    if main.IS_TEST == True:
        return ManagerApp.get_json_data()["bot_token_test"]
    else:
        return ManagerApp.get_json_data()["bot_token"]




BOT_TOKEN = get_token_bot()
admin_chat_id = "873327794"
# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize tg_bot and dispatcher
bot_telegram = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot_telegram)

process_queue_shared = multiprocessing.Manager().list()


@dp.callback_query_handler()
async def callback_handler(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    from manager.control import Control
    if int(Control().get_user_status_db(chat_id)) == 1:
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

                        client_info = str(count) + ") " + str(item.get("FIO")) + " | Телефон: " + str(
                            item.get("PHONE")) + " | Дата для записи: " + str(
                            item.get("ORDER_DATE"))
                        print("text=" + client_info)
                        if count == len(clients):
                            keyboard = InlineKeyboardMarkup(row_width=1).add(yes, no)
                        await bot_telegram.send_message(chat_id=chat_id, text=client_info,
                                                        reply_markup=keyboard)
                        count += 1
                except Exception as e:
                    print(e)
            else:
                await bot_telegram.send_message(chat_id=chat_id,
                                                text="Нет запущенных процессов по клиентам")
        elif callback.data == Menu.help_button:
            await send_help_menu(callback.message.chat.id)
        elif callback.data == Menu.stop_all_process_button:
            if len(process_queue_shared) > 0:
                yes = InlineKeyboardButton("Да", callback_data="/stopall")
                no = InlineKeyboardButton("Нет", callback_data="<-Назад")
                keyboard = InlineKeyboardMarkup().add(yes, no)
                await bot_telegram.send_message(chat_id=chat_id,
                                                text="Вы уверены, что хотите завершить все процессы?",
                                                reply_markup=keyboard)

            else:
                await bot_telegram.send_message(chat_id=chat_id,
                                                text="Нет запущенных процессов по клиентам")
        elif callback.data == "/stopall":
            await stop_process(callback)

        elif callback.data == "/enablemonitoring":
            Control().enable_monitoring()
            await bot_telegram.send_message(chat_id=chat_id, text="Мониторинг включен")

        elif callback.data == "Назад":
            clients_button = InlineKeyboardButton(Menu.clients_button, callback_data=Menu.clients_button)
            help_button = InlineKeyboardButton(Menu.help_button, callback_data=Menu.help_button)
            keyboard = InlineKeyboardMarkup(row_width=2).add(clients_button, help_button)
            await bot_telegram.send_message(chat_id=chat_id, text=Menu.main_menu,
                                            reply_markup=keyboard)
        elif callback.data == "<-Назад" or callback.data == Menu.clients_button:
            print("Меню клиенты")
            keyboard: InlineKeyboardMarkup = get_clients_keyboard()
            await bot_telegram.send_message(chat_id=chat_id, text=Menu.clients_button,
                                            reply_markup=keyboard)

        elif callback.data.__contains__("Stop_"):
            try:
                phone_client = callback.data.replace("Stop_", "")
                for index, client_process in enumerate(process_queue_shared):
                    if str(client_process.get("PHONE")) == str(phone_client):
                        ManagerApp.logger_main.info("Set ACTIVE=0 for {}".format(phone_client))
                        print("BOT: process_queue_shared1=", process_queue_shared)
                        client_process["ACTIVE"] = 0
                        process_queue_shared[index] = client_process
                        Google_Doc().delete_row_gspread(phone_client)
                        print("BOT: client_process=", client_process)
                        # process_queue_shared.append({'PHONE': 77777777, 'ACTIVE': 1})
                        print("BOT: process_queue_shared2=", process_queue_shared)
                await bot_telegram.send_message(chat_id=chat_id, text="Процесс остановлен")
            except Exception as e:
                print(e)

    else:
        await bot_telegram.send_message(chat_id=chat_id, text="У вас отсутствуют права для пользования ботом.\n"
                                                              " Для получения доступа обратитесь к @as_alekseev")


async def stop_process(callback):
    from manager.control import Control
    try:
        await bot_telegram.send_message(chat_id=callback.message.chat.id,
                                        text="Остановка процессов...")
        # for index, client_process in enumerate(process_queue_shared):
        #     ManagerApp.logger_main.info("Set ACTIVE=0 for all")
        #     Control().disable_monitoring()
        #     client_process["ACTIVE"] = 0
        #     process_queue_shared[index] = client_process
        #     print("BOT: client_process=", client_process)
        #     print("BOT: process_queue_shared2=", process_queue_shared)
        #     sleep(3)
        # for index in range(10):
        #     if len(Data_Base.execute_select_query("select* from sessions")) > 0:
        #         sleep(5)
        # Control().execute_bash_command("pkill -9 -f chromedriver")
        # Control().execute_bash_command("pkill -9 -f chrome")
        Control().stop_all_process(disable_monitoring=True)

        await bot_telegram.send_message(chat_id=callback.message.chat.id,
                                        text="Процессы мониторинга остановлены")
    except Exception as e:
        print(e)


# @dp.register_message_handler(on_msg :types.ContentType.all())
@dp.message_handler()
async def message_handler(message: types.Message):
    from manager.control import Control
    print(process_queue_shared)
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if message.text == "/start":
        print("Вход")
        chatid = message.from_user.id
        print(chatid)
        date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        username = message.chat.username

        name_user = message.from_user.first_name
        fio = name_user
        language_code = message.from_user.language_code
        print(language_code)
        action_id = "0"

        if len(Data_Base.execute_select_query("select* from configuration where chatid=%s" % chatid)) == 0:
            print("Вставляем")
            Data_Base.execute_process(
                "insert into configuration (chatid, date, username, fio, language_code, action_id) values ('%s', '%s', '%s', '%s', '%s', '%s')" % (
                    chatid, date, username, fio, language_code, action_id))
        btn1 = types.KeyboardButton(Menu.clients_button)
        btn2 = types.KeyboardButton(Menu.help_button)
        keyboard.add(btn1, btn2)
        await message.answer("Главное меню", reply_markup=keyboard)

    if int(Control().get_user_status_db(chat_id)) == 1:
        if message.text == Menu.clients_button:
            keyboard = get_clients_keyboard()
            await message.answer(message.text, reply_markup=keyboard)
        elif message.text == Menu.help_button:
            await send_help_menu(message.chat.id)
    else:
        await bot_telegram.send_message(chat_id=chat_id, text="У вас отсутствуют права для пользования ботом.\n"
                                                              " Для получения доступа обратитесь к @as_alekseev")

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
        url=ManagerApp.get_json_data()["document_url"],
        callback_data=Menu.open_client_file_button)
    back_button = InlineKeyboardButton("Назад", callback_data="Назад")
    if int(Data_Base.get_data_by_query("select* from settings")[0].get("MONITORING_STATUS")) == 0:
        keyboard = InlineKeyboardMarkup(row_width=1).add(run_monitoring, process_button, stop_process_button,
                                                         open_client_file_button,
                                                         back_button)
    else:
        keyboard = InlineKeyboardMarkup(row_width=1).add(process_button, stop_process_button, open_client_file_button,
                                                         back_button)
    return keyboard


async def on_startup(_):
    try:
        await bot_telegram.send_message(admin_chat_id, "Запустился")
    except Exception as e:
        ManagerApp.logger_main.warning(e)


async def send_text(text):
    await bot_telegram.send_message(chat_id=admin_chat_id, text=text)


def send_message(chat_id, text):
    send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + text
    response = requests.get(send_text)
    return response.json()


def start_bot(process_queue):
    from manager.control import Control
    ManagerApp.logger_main.info("Start bot")

    starter_bot.process_queue_shared = process_queue
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


def send_file(path_file, chat_id):
    from manager.control import Control
    ManagerApp.logger_client.info("Send file to telegram")
    Control().execute_bash_command(
        (("curl -F document=@%s https://api.telegram.org/bot" + BOT_TOKEN + "/sendDocument?chat_id=") + chat_id) % path_file)
