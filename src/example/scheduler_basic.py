import asyncio
import datetime
import json

class SchedulerBasic:
    FLAG = True
    later: datetime.datetime
    
    def __init__(self, func):
        self.func = func

    def is_working_hour(self):
        now = datetime.datetime.now()
        if self.FLAG:
            self.later = now + datetime.timedelta(seconds=5)
            self.FLAG = False
        return now < self.later

    async def start(self, message, repeat_time):
        while True:
            if self.is_working_hour():
                response = await self.func(message)
                await asyncio.sleep(repeat_time)
                print("response: ", response)
            else:
                print("working hour가 아님 waiting!!")
                await asyncio.sleep(4)
                self.FLAG = True


async def target_function(message):
    print(message)
    return json.dumps({"status": "success", "data": "Hello, world!"}) # test를 위한 코드

async def main():
    print("시작")
    repeat_time = 2
    scheduler_basic = SchedulerBasic(target_function)
    task = asyncio.create_task(scheduler_basic.start("전달된 메세지쓰", repeat_time))
    try:
        await task
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    asyncio.run(main())