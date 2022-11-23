import time
from functools import wraps


def retry(function=None, max_retries: int = 3, delay: (int, float) = 0, exceptions: bool = False,
          position: bool = True):
    """
        :param position: 重试带函数执行的位置: True:在执行函数前面， False:在执行函数后面。
        :param function: 重试带函数执行执行。
        :param max_retries: 最多重试次数。
        :param delay: 每次重试的延迟，单位秒。
        :param exceptions: 输出触发重试的异常
    """

    def outter(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_count = max_retries
            try:
                result = func(*args, **kwargs)
                return result

            except Exception as e:
                if exceptions:
                    print(e)
                while True:
                    time.sleep(delay)
                    if retry_count < 1:
                        break
                    print('正常重试,剩余重试次数:', retry_count - 1)

                    try:
                        if position is True:
                            if function:
                                function()
                        result = func(*args, **kwargs)
                        return result
                    except Exception as e:
                        if exceptions:
                            print(e)
                    finally:
                        if position is False:
                            if function:
                                function()
                        retry_count -= 1

        return wrapper

    return outter
