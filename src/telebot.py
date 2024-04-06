from private_data import TOKEN_ID, CHAT_ID
import telegram
import asyncio
from treasury_stock_data import TreasuryStock

bot = telegram.Bot(token=TOKEN_ID)

async def main():
    treasury_stock = TreasuryStock()
    print(treasury_stock.get_stock_data())
    # await bot.send_message(chat_id=CHAT_ID, text="hello")

asyncio.run(main())