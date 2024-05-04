import signal
import time
from datetime import datetime, time, timedelta

REPEAT_TIME_FOR_CHECK = 60 * 2
START_HOUR = 9
START_MINUTE = 0
END_HOUR = 15
END_MINUTE = 30

class TeleScheduler:
    __repeat_time_for_check = REPEAT_TIME_FOR_CHECK
    def __init__(self, func, message = "") -> None:
        handler = self.__alarm_handler_factory(func, message)
        # set up signal handler
        signal.signal(signal.SIGALRM, handler)
    
    def is_working_hour(self) -> bool:
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

    def __alarm_handler_factory(self, func, message):
        # signum: identifier
        # frame: current stack frame. execution state를 나타내는 object
        def __alarm_handler(signum, frame) -> None:
            if self.is_working_hour():
                func(message)
                signal.alarm(self.__repeat_time_for_check)
            else:
                self.wait_until_start()
        return __alarm_handler

    def start_alarm(self) -> None:
        print("==== 장 시작 ====")
        signal.alarm(self.__repeat_time_for_check)

    def wait_until_start(self) -> None:
        print("==== 장 마감 후 sleep 중 ====\n")
        time_left_for_start = self.__get_time_left_for_start()
        # while not self.is_working_hour():
        time.sleep(time_left_for_start)
        if not self.is_working_hour():
            self.wait_until_start()
        self.start_alarm()


## 사용 예

# def main():
#     scheduler_signal = TeleScheduler()
#     print("scheduler 시작")
#     if scheduler_signal.is_working_hour():
#         scheduler_signal.start_alarm()
#     else:
#         scheduler_signal.wait_until_start()

#     try:
#         while True:
#             time.sleep(1) # infinite loop for Program running
#     except KeyboardInterrupt:
#         print("프로그램 종료")

# if __name__ == "__main__":
#     main()