from retrying import retry
from random import randint


@retry(stop_max_attempt_number=200)
def get_random():
    int_r = randint(0, 100)
    if int_r > 0:
        print(f"该随机数等于{int_r}")
        raise IOError("该随机数大于0")
    else:
        return int_r


print(f"该随机数等于{get_random()}")
