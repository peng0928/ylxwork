from multiprocessing import Process
import os, time
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(20)


def func():
    print('这是一个子进程——>进程号：', os.getpid(), '  主进程号：', os.getppid())
    while True:
        for i in range(60):
            print('a', i, time.sleep(i))


def run():
    p = Process(target=func)
    p.start()
    p.join()

if __name__ == '__main__':
    print('这是主进程——>进程号：', os.getpid(), '  主进程号（pycharm）：', os.getppid())
    # 实例化一个子进程对象

    executor.submit(run)

    print('执行了完了主进程的内容')


    for i in range(60):
        print(i, time.sleep(i))
