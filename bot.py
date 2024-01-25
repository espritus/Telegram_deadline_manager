from gettext import dpgettext
from aiogram import types

from botHandler import BotHandler

from config_reader import config

if __name__ == '__main__':
    bt = BotHandler(config.BOT_TOKEN.get_secret_value())

    @bt.dp.message_handler(commands=['start'])
    async def send_start_msg(message: types.Message):
        user_id = message.from_user.id
        await bt.bot.send_message(user_id, f'{message.from_user.first_name}, добро пожаловать! отправь мне пожалуйста .xlsx в формате "событие" и "дедлайн" в Excel.')

    @bt.dp.message_handler(content_types=['document'])
    async def handle_excel_file(message: types.Message):
        await bt.handle_excel_file(message)

    @bt.dp.message_handler(commands=['display'])
    async def display_dates_and_names_handler(message: types.Message):
        await bt.display_dates_and_names_handler(message)

    @bt.dp.message_handler(commands=['send_notif'])
    async def check_and_send_deadline_notification(message: types.Message):
        await bt.check_and_send_deadline_notification(message)

    @bt.dp.message_handler(commands=['delete_file'])
    async def delete_file(message: types.Message):
        await bt.delete_file(message)

    bt.start_polling()
