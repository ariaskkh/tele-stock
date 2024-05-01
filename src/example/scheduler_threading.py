import threading
import time

class Scheduler:
    def __init__(self) -> None:
        self.end_time = 0
        self.__update_working_hour()
        self.timer: threading.Timer = None

    def __some_function(self) -> None:
        print('특정 동작 실행 중')

    # 장 열리는 시간으로 다시 설정
    def __update_working_hour(self) -> None:
        self.end_time = time.time() - 5

    def is_working_hour(self) -> bool:
        return time.time() <= self.end_time
    
    def __get_local_time(self, end_time) -> time:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))

    def wait_until_start(self) -> None:
        time_left_for_start = 10 # 장 시작 시간 - 현재 시간
        while not self.is_working_hour():
            print("==== 장 마감 후 sleep 중 ====\n")
            time.sleep(time_left_for_start)
            self.__update_working_hour()
        print("==== 장 시작 ====")
        self.threading_timer()
            

    def threading_timer(self) -> None:
        print("==== threading timer 시작 ====")
        repeating_time = 2 # 공시 api call 반복 간격
        self.timer = threading.Timer(repeating_time, self.threading_timer) # 2초 간격 함수 실행
        self.timer.start()
        self.__some_function() # 실질적 실행
        if not self.is_working_hour(): # 장 마감 시
            self.timer.cancel()
            print("==== threading timer 종료 - end_time:", self.__get_local_time(self.end_time), "====")
            self.wait_until_start()
            return


def main():
    scheduler = Scheduler()
    print("scheduler 시작")
    if scheduler.is_working_hour():
        print("==== 장 시작 ====")
        scheduler.threading_timer()
    else:
        scheduler.wait_until_start()

if __name__ == "__main__":
    main()