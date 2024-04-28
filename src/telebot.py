from private_data import TOKEN_ID, CHAT_ID
from telegram.ext import ApplicationBuilder, ContextTypes
from treasury_stock_data import TreasuryStock
import datetime
import asyncio

REPEAT_TIME = 10 # 초 단위

async def sendTreasoryStockMessage(context: ContextTypes.DEFAULT_TYPE) -> None:
    print("message")
    if not is_working_hours():
        print("message - stop")
        # await context.application.stop()
        raise asyncio.CancelledError("Outside working hours")
    
    treasury_stock = TreasuryStock()
    treasury_stock_tele_message = treasury_stock.get_stock_tele_messages()
    if(treasury_stock_tele_message != None):    
        for message in treasury_stock_tele_message:
            await context.bot.send_message(chat_id = CHAT_ID, text = message)

def is_working_hours():
    now = datetime.datetime.now().time()
    # start_time = datetime.time(9, 0) # 9 am
    # end_time = datetime.time(15, 30) # 3:30 pm
    # return start_time <= now <= end_time 
    return now <= datetime.time(0, 22)

async def start_tele_bot():
    application = ApplicationBuilder().token(TOKEN_ID).build()
    repeating_job = None
    while True:
        if is_working_hours():
            print("공시 알림 시작")
            await application.initialize()
            await application.start()
            # JobQueue: APScheduler wrapper
            repeating_job = application.job_queue.run_repeating(sendTreasoryStockMessage, interval=REPEAT_TIME, first=1)
            application.run_polling()
            await asyncio.sleep(1)  # Sleep briefly to allow the bot to start
            if repeating_job:
                repeating_job.schedule_removal() # cancel the repeating job
            await application.stop()
            print("공시 알림 종료")
        else:
            print("공시 알림 sleep")
            # now = datetime.now()
            # tomorrow = now + timedelta(days = 1)
            # start_of_next_day = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9, 0)
            # time_until_next_day = start_of_next_day - now
            # await asyncio.sleep(time_until_next_day.total_seconds())
            
            await asyncio.sleep(5)

def main():
    asyncio.run(start_tele_bot())

if __name__ == "__main__":
    main()
