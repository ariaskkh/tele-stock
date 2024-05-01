import signal
import time

class SchedulerSignal:
    def __init__(self) -> None:
        # set up signal handler
        signal.signal(signal.SIGALRM, self.__alarm_handler)
        self.repeat_time = 2
        self.end_time = time.time() + 5
    
    def is_working_hour(self) -> bool:
        # return time.time() < self.end_time
        return False

    def __update_working_hour(self) -> None:
        self.end_time = time.time() + 5

    # signum: identifier
    # frame: current stack frame. execution state를 나타내는 object
    def __alarm_handler(self, signum, frame) -> None:
        print("하고 싶은 다 해~")
        if self.is_working_hour():
            signal.alarm(self.repeat_time)
        else:
            self.wait_until_start()

    def start_alarm(self) -> None:
        print("==== 장 시작 ====")
        signal.alarm(self.repeat_time)

    def wait_until_start(self) -> None:
        print("==== 장 마감 후 sleep 중 ====\n")
        time_left_for_start = 5
        while not self.is_working_hour():
            time.sleep(time_left_for_start)
            self.__update_working_hour()
        self.start_alarm()


def main():
    scheduler_signal = SchedulerSignal()
    print("scheduler 시작")
    if scheduler_signal.is_working_hour():
        scheduler_signal.start_alarm()
    else:
        scheduler_signal.wait_until_start()

    try:
        while True:
            time.sleep(1) # infinite loop for Program running
    except KeyboardInterrupt:
        print("프로그램 종료")

if __name__ == "__main__":
    main()