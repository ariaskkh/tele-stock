import signal
import time as timer
from datetime import datetime, time, timedelta
import asyncio

REPEAT_TIME_FOR_CHECK = 2
START_HOUR = 9
START_MINUTE = 0
END_HOUR = 15
END_MINUTE = 30

class TeleScheduler:
    __repeat_time_for_check = REPEAT_TIME_FOR_CHECK

    def __init__(self, loop, func, message = "") -> None:
        handler = self.__alarm_handler_factory(loop, func, message)
        # set up signal handler
        signal.signal(signal.SIGALRM, handler)
    
    def __is_working_hour(self) -> bool:
        now = datetime.now().time()
        start_time = time(START_HOUR, START_MINUTE) # 9 am
        end_time = time(END_HOUR, END_MINUTE) # 3:30 pm
        return start_time <= now < end_time

    def __get_time_left_for_start(self) -> int:
        now = datetime.now()
        tomorrow = now + timedelta(days = 1)
        # 주말, 공휴일 예외처리 필요
        next_start_time = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9, 0)
        time_left_for_next_start: timedelta = next_start_time - now
        return time_left_for_next_start.total_seconds()

    def __alarm_handler_factory(self, loop, func, params):
        # signum: identifier
        # frame: current stack frame. execution state를 나타내는 object
        def __alarm_handler(signum, frame) -> None:
            if self.__is_working_hour():
                asyncio.run_coroutine_threadsafe(func(params), loop)
                signal.alarm(self.__repeat_time_for_check)
            else:
                self.__wait_until_start()
        return __alarm_handler

    def start_alarm(self) -> None:
        if self.__is_working_hour():
            print("==== 장 시작 ====")
            signal.alarm(self.__repeat_time_for_check)
        else:
            print("==== 장 마감 후 sleep 중 ====\n")
            self.__wait_until_start()

    def __wait_until_start(self) -> None:
        timer.sleep(self.__get_time_left_for_start())
        self.start_alarm()