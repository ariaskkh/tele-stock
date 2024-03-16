from private_data import TOKEN_ID, CHAT_ID
import telegram
import asyncio

bot = telegram.Bot(token=TOKEN_ID)

async def main():
    await bot.send_message(chat_id=CHAT_ID, text="hello")

asyncio.run(main())