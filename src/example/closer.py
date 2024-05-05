import signal
import asyncio

async def targetFunction(message):
    print("CLOSER SUCCESS")
    print(message)
    await asyncio.sleep(1)

# Closer
def signal_handler_factory(loop, func, message, repeat_time):
    print("signal_handler_factory")
    def signal_handler(signum, frame):
        asyncio.run_coroutine_threadsafe(func(message), loop)
        signal.alarm(repeat_time)
    return signal_handler

def main():
    print("시작")
    repeat_time = 2
    loop = asyncio.get_event_loop()
    handler = signal_handler_factory(loop, targetFunction, "전달된 메세지쓰", repeat_time)
    
    signal.signal(signal.SIGALRM, handler) # alarm 설정
    signal.alarm(repeat_time) # alarm 부르기

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

if __name__ == "__main__":
    main()
