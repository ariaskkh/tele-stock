from private_data import TOKEN_ID, CHAT_ID
import telegram
import asyncio
from treasury_stock_data import TreasuryStock

bot = telegram.Bot(token=TOKEN_ID)

async def main():
    treasury_stock = TreasuryStock()
    treasury_stock_data = treasury_stock.get_stock_data()
    for data in treasury_stock_data:
        await bot.send_message(chat_id = CHAT_ID, text = data)
asyncio.run(main())