import multiprocessing
from datetime import datetime
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

API_TOKEN = '5452785880:AAHr6nD0Es7t_rv9j-_JDNwPOKuBc78onrY'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize tg_bot and dispatcher
bot_telegram = Bot(token=API_TOKEN)
dp = Dispatcher(bot_telegram)

process_queue_shared = multiprocessing.Manager().list()

@dp.callback_query_handler()
async def callback_handler(callback: types.CallbackQuery):
    from manager.control import Control
    print("Callback")
    try:
        print("Threads="+str())
    except Exception as e:
        print(e)
    if callback.data == Menu.show_process_button:
        print("Show process: ")
        clients = Data_Base.get_data_by_query("select* from sessions")
        print("clients="+str(clients))
        if len(clients)>0:
            try:
                count = 1
                for item in clients:
                    button = InlineKeyboardButton("Остановить", callback_data="Stop_" + str(item.get("PHONE")))
                    keyboard = InlineKeyboardMarkup(row_width=1).add(button)

                    client_info = str(count) + ") " + str(item.get("FIO")) + "\nДата записи: " + str(
                        item.get("ORDER_DATE"))
                    print("text=" + client_info)
                    await bot_telegram.send_message(chat_id=callback.message.chat.id, text=client_info,
                                                    reply_markup=keyboard)
                    count += 1
            except Exception as e:
                print(e)
        else:
            await bot_telegram.send_message(chat_id=callback.message.chat.id, text="Нет запущенных процессов по клиентам")
    elif callback.data.__contains__("Stop_"):
        try:
            phone_client = callback.data.replace("Stop_", "")
            for index, client_process in enumerate(process_queue_shared):
                if str(client_process.get("PHONE")) == str(phone_client):
                    ManagerApp.get_logger().info("Set ACTIVE=0 for " + str(phone_client))
                    print("BOT: process_queue_shared1=", process_queue_shared)
                    client_process["ACTIVE"] = 0
                    process_queue_shared[index]=client_process
                    Google_Doc.delete_row_from_doc(phone_client)
                    print("BOT: client_process=",client_process)
                    #process_queue_shared.append({'PHONE': 77777777, 'ACTIVE': 1})
                    print("BOT: process_queue_shared2=", process_queue_shared)
        except Exception as e:
            print(e)


        #print("BOT: ThreadList=",bot_tg.process_queue.get())





        #await bot.send_message(callback.message.chat.id, client_info)


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
        fio = message.from_user.first_name + " "+ message.from_user.last_name
        language_code = message.from_user.language_code
        action_id = "0"
        Data_Base().exec_query(
            "insert into configuration (chatid, date, username, fio, language_code, action_id) values ('%s', '%s', '%s', '%s', '%s', '%s')" % (
                chatid, date, username, fio, language_code, action_id))
    elif message.text == Menu.clients_button:

        process_button = InlineKeyboardButton(Menu.show_process_button, callback_data=Menu.show_process_button)
        stop_process_button = InlineKeyboardButton(Menu.stop_process_button, callback_data=Menu.stop_process_button)
        open_client_file_button = InlineKeyboardButton(
            Menu.open_client_file_button,
            url="https://docs.google.com/spreadsheets/d/1qu-TfbUYCaWAmS65yya2yYKttBTTBnWpLjAF5grQtNY/edit#gid=0",
            callback_data=Menu.open_client_file_button)
        back_button = InlineKeyboardButton(Menu.back_button, callback_data=Menu.back_button)
        keyboard = InlineKeyboardMarkup(row_width=1).add(process_button, stop_process_button, open_client_file_button, back_button)

        await message.answer(message.text, reply_markup=keyboard)
    else:
        btn1 = types.KeyboardButton(Menu.clients_button)
        btn2 = types.KeyboardButton(Menu.help_button)
        keyboard.add(btn1, btn2)
        await message.answer("Главное меню", reply_markup=keyboard)



def start_bot(process_queue):
    from manager.control import Control
    Control().delete_sessions()
    starter_bot.process_queue_shared = process_queue
    executor.start_polling(dp, skip_updates=True)





