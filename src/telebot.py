from private_data import TOKEN_ID, CHAT_ID
import telegram
from treasury_stock_data import TreasuryStock
import asyncio

class TeleBot:
    treasury_stock: TreasuryStock
    def __init__(self) -> None:
        self.bot = telegram.Bot(token=TOKEN_ID)

    def add_treasury_stock(self) -> None:
        self.treasury_stock = TreasuryStock()
    
    async def send_stock_tele_message(self) -> None:
        if self.treasury_stock:
            treasury_stock_tele_message = self.__get_stock_tele_message()
            if treasury_stock_tele_message != None:
                for message in treasury_stock_tele_message:
                    await self.bot.send_message(chat_id = CHAT_ID, text = message)
        else:
            print("Treasury_stock 인스턴스가 생성되지 않았습니다.")

    def __get_stock_tele_message(self) -> list:
        return self.treasury_stock.get_stock_tele_messages()
    

async def main():
    print("==== 프로그램 시작 !! ====")

    telebot = TeleBot()
    telebot.add_treasury_stock()
    await telebot.send_stock_tele_message()

    print("==== 프로그램 종료 !! ====")

if __name__ == "__main__":
    asyncio.run(main())
