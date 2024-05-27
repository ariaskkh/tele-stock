import signal
import time as timer
from datetime import datetime, time, timedelta
import asyncio

REPEAT_TIME_FOR_CHECK = 2
START_HOUR = 9
START_MINUTE = 0
END_HOUR = 15
END_MINUTE = 30

class IntervalExecutor:
    def __init__(self, func, message = "") -> None:
        self.loop = asyncio.get_event_loop()
        self.func = func
        self.message = message
        # set up signal handler
        signal.signal(signal.SIGALRM, self.__alarm_handler)
    
    def __is_working_hour(self) -> bool:
        # return True
        now = datetime.now().time()
        start_time = time(START_HOUR, START_MINUTE) # 9 am
        end_time = time(END_HOUR, END_MINUTE) # 3:30 pm
        return start_time <= now < end_time
    
    def __alarm_handler(self, signum, frame) -> None:
        if self.__is_working_hour():
            asyncio.run_coroutine_threadsafe(self.func(self.message), self.loop)
            signal.alarm(REPEAT_TIME_FOR_CHECK)
        else:
            print("==== 장 마감 종료 ====")
            
    def start_alarm(self) -> None:
        print("==== 장 시작 ====")
        signal.alarm(REPEAT_TIME_FOR_CHECK)