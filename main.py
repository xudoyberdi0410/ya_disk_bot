import asyncio
import logging
import sys
from os import getenv
import io

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, TelegramObject
from disk.YaDisk import YaDisk
from typing import Callable, Dict, Any, Awaitable

load_dotenv()
TOKEN = getenv("BOT_TOKEN")
ADMIN = 759839831
with open("users.txt", "r") as file:
    users = file.read().split(",")

dp = Dispatcher()

class AuthMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        if str(event.from_user.id) in users or event.from_user.id == ADMIN:
            return await handler(event, data)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.reply("саша лох")

@dp.message(Command("add"))
async def add_new_user(message: Message, command: Command) -> None:
    if message.from_user.id == ADMIN:
        new_user_id = str(command.args)
        with open("users.txt", "a") as file:
            file.write(f"{new_user_id},")
        users.append(str(new_user_id))
        await message.reply("Пользователь добавлен!")
    else:
        await message.reply("У вас недостаточно прав!")

@dp.message(F.document)
async def document_handler(message: Message, bot: Bot, disk: YaDisk) -> None:
    await message.reply("Начинается загрузка")
    document = message.document
    result: io.BytesIO = await bot.download(document.file_id)
    file_path: str = f"test/{document.file_name}"
    upload_file = await disk.upload_file(result.read(), document.file_name, to_folder="test")
    if not upload_file:
        await message.reply("Ошибка загрузки файла!")
        return
    await disk.do_publish(file_path)
    public_url = await disk.get_info(file_path, fields=["public_url"])
    await message.reply(f"Загрузка завершена!\nСсылка на файл: {public_url["public_url"]}")

async def main() -> None:
    disk = YaDisk()
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # add middleware
    dp.message.middleware(AuthMiddleware())
    await dp.start_polling(bot, disk=disk)

if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())