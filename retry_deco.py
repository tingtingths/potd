import time


def retry(tries=4, delay=2):  # 2 seconds
    def decorator(func):
        def wrapper(*args):
            _tries = tries
            while _tries != 0:
                try:
                    return func(*args)
                    break
                except Exception as e:
                    _tries -= 1
                    print("Error at retry(): {0} attempt(s) left.\n  {1}  ".format(str(_tries), str(e)))
                    if _tries != 0:
                        time.sleep(delay)

        return wrapper

    return decorator
