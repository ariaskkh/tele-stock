import time
import signal

def targetFunction(message):
    print("CLOSER SUCCESS")
    print(message)

# Closer
def signal_handler_factory(func, message, repeat_time):
    print("signal_handler_factory")
    def signal_handler(signum, frame):
        func(message)
        signal.alarm(repeat_time)
    return signal_handler

def main():
    print("시작")
    repeat_time = 2
    handler = signal_handler_factory(targetFunction, "전달된 메세지쓰", repeat_time)
    
    signal.signal(signal.SIGALRM, handler) # alarm 설정
    signal.alarm(repeat_time) # alarm 부르기

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
