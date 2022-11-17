import time
from functools import wraps


def retry(max_retries: int = 3, delay: (int, float) = 0, exceptions: bool = False):
    """
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
                        print('达到最大重试次数, 退出！')
                        break
                    print('正常重试,剩余重试次数:', retry_count - 1)

                    try:
                        result = func(*args, **kwargs)
                        return result
                    except Exception as e:
                        if exceptions:
                            print(e)
                    finally:
                        retry_count -= 1

        return wrapper
    return outter
