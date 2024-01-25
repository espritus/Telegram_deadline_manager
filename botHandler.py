import asyncio
from aiogram.utils import executor
from aiogram import Bot
from aiogram.dispatcher import Dispatcher

import pandas as pd
from datetime import datetime, timedelta
import logging
from notifiers import get_notifier

from config_reader import config

# Logging -----> (Регистрации информации о работе бота) (Администрация)
logging.basicConfig(level=logging.INFO)


class BotHandler:
    def __init__(self, bot_token):
        self.data = None
        self.bot = Bot(bot_token)
        self.dp = Dispatcher(self.bot)
        self.token = bot_token

    def start_polling(self):
        executor.start_polling(self.dp, skip_updates=True)

 # Обратная связь -----> (Обработка файлов)

    async def handle_excel_file(self, message):
        try:
            if message.document.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                file_info = await self.bot.get_file(message.document.file_id)
                file_path = file_info.file_path
                self.data = pd.read_excel(
                    f'https://api.telegram.org/file/bot{self.token}/{file_path}')

                await self.bot.send_message(message.from_user.id, "Файл успешно обработан!")
            else:
                await self.bot.send_message(message.from_user.id, "Пожалуйста, отправьте файл в формате Excel (xlsx).")
        except Exception as e:
            logging.error(f"Error handling Excel file: {e}")
            await self.bot.send_message(message.from_user.id, "Произошла ошибка при обработке файла.")


#   Обратная связь -----> (Показ результата обработанного файла по срочности)

    async def display_dates_and_names_handler(self, message):
        if self.data is not None:
            message_content = ""
            current_date = datetime.now()
            filtered_data = [(date, name) for date, name in zip(
                self.data[config.datesColumn], self.data[config.namesColumn]) if date >= current_date]
            sorted_data = sorted(filtered_data)

            for idx, (date_value, name_value) in enumerate(sorted_data):
                message_content += f"{idx + 1}. Дата: {date_value.strftime('%d.%m.%Y')}, Событие: {name_value}\n"
            await self.bot.send_message(message.from_user.id, message_content)
        else:
            await self.bot.send_message(message.from_user.id,
                                        "Файл еще не был загружен.")


#  Обратная связь по дедлайну -----> (Результат обработанного файла)

    async def check_and_send_deadline_notification(self, message):
        while True:  # Бесконечный цикл для периодического выполнения
            if self.data is not None:
                for idx, x in enumerate(self.data[config.datesColumn]):
                    deadline = x - datetime.now()
                    if timedelta(days=0) <= deadline <= timedelta(days=config.daysLeft):
                        dead_key_name = self.data[config.namesColumn].loc[idx]
                        dead_time = deadline.days

                        if dead_time == 0:
                            dead_time = str(deadline.seconds /
                                            3600).partition('.')[0]
                            await self.send_msg(
                                message.from_user.id, f'🔥 ВНИМАНИЕ\nВыходит срок: {dead_key_name}\nОсталось: {dead_time} ч.\nСрок: {x.strftime("%d.%m.%Y")}')
                        else:
                            await self.send_msg(
                                message.from_user.id, f'🔥 ВНИМАНИЕ\nВыходит срок: {dead_key_name}\nОсталось: {dead_time} дн.\nСрок: {x.strftime("%d.%m.%Y")}')
            else:
                await self.bot.send_message(message.from_user.id,
                                            "Файл еще не был загружен.")

            await asyncio.sleep(86400)  # Ожидание 1 дня (в секундах)

    async def send_msg(self, user_id, text):
        await self.bot.send_message(user_id, text)


# Обратная связь для удаления-----> (Удаление excel )

    def delete_file(self, message):
        if self.data is not None:
            self.data = None
            self.bot.send_message(message.from_user.id, "Файл удален.")
        else:
            self.bot.send_message(message.from_user.id,
                                  "Файл еще не был загружен.")
