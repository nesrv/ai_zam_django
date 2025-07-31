from aiogram import Bot, Dispatcher, types

bot = Bot(token="ВАШ_ТОКЕН")
dp = Dispatcher(bot)

@dp.message_handler()
async def get_chat_id(message: types.Message):
    chat_id = message.chat.id
    await message.reply(f"ID этого чата: {chat_id}")

executor.start_polling(dp)


TELEGRAM_TOKEN=7836693206:AAFgvbLhQSuDCCWPr5zaafDn0W_-CGF0yGk

curl.exe -X GET "https://api.telegram.org/bot7836693206:AAFgvbLhQSuDCCWPr5zaafDn0W_-CGF0yGk/getUpdates"

# -4916602123