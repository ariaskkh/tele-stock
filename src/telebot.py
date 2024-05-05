from private_data import TOKEN_ID, CHAT_ID
import telegram
from tele_scheduler import TeleScheduler
from treasury_stock_data import TreasuryStock
import asyncio

class TeleBot:
    treasury_stock: TreasuryStock
    scheduler: TeleScheduler
    
    def __init__(self, loop) -> None:
        self.bot = telegram.Bot(token=TOKEN_ID)
        self.scheduler = TeleScheduler(loop, self.__send_message)

    def start_sending_message(self) -> None:
        self.scheduler.start_alarm()

    async def __send_message(self, params = None) -> None:
        self.treasury_stock = TreasuryStock()
        treasury_stock_tele_message = self.__get_stock_tele_message()
        if treasury_stock_tele_message != None:
            for message in treasury_stock_tele_message:
                await self.bot.send_message(chat_id = CHAT_ID, text = message)

    def __get_stock_tele_message(self) -> list:
        return self.treasury_stock.get_stock_tele_messages()

def main():
    print("==== 프로그램 시작 !! ====")

    loop = asyncio.get_event_loop()
    telebot = TeleBot(loop)
    telebot.start_sending_message()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("==== 프로그램 종료 !! ====")
    finally:
        loop.close()

if __name__ == "__main__":
    main()
