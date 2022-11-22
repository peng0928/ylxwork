import signal
import time
import datetime

def handler(sig, frame):
    print(datetime.datetime.now())
    print("handler function")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    print(datetime.datetime.now())
    signal.alarm(5)
    time.sleep(10)
    print(datetime.datetime.now())
    print("main function")