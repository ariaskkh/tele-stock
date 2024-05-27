from private_data import TOKEN_ID, CHAT_ID
import telegram
from interval_executor import IntervalExecutor
from treasury_stock_data import TreasuryStock

class TeleBot:
    treasury_stock: TreasuryStock
    intervalExecutor: IntervalExecutor
    
    def __init__(self) -> None:
        self.bot = telegram.Bot(token=TOKEN_ID)
        self.intervalExecutor = IntervalExecutor(self.__send_message)
        
    async def __send_message(self, params = None) -> None:
        self.treasury_stock = TreasuryStock()
        treasury_stock_tele_message = self.__get_stock_tele_message()
        if treasury_stock_tele_message != None:
            for message in treasury_stock_tele_message:
                await self.bot.send_message(chat_id = CHAT_ID, text = message)

    def __get_stock_tele_message(self) -> list:
        return self.treasury_stock.get_stock_tele_messages()
    
    def start(self) -> None:
        self.intervalExecutor.start_alarm()
        self.intervalExecutor.loop.run_forever()

    def end(self) -> None: 
        self.intervalExecutor.loop.close()

def main():
    print("==== 프로그램 시작 !! ====")
    telebot = TeleBot()

    try:
        telebot.start()
    except KeyboardInterrupt:
        print("==== 프로그램 종료 !! ====")
        telebot.end()

if __name__ == "__main__":
    main()
