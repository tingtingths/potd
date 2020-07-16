import time


def retry(attempts=4, delay=2):  # 2 seconds
    def decorator(func):
        def wrapper(*args):
            _attempts = attempts
            while _attempts != 0:
                try:
                    return func(*args)
                except Exception as e:
                    _attempts -= 1
                    print("Error at retry(): {0} attempt(s) left.\n  {1}  ".format(str(_attempts), str(e)))
                    if _attempts != 0:
                        time.sleep(delay)

        return wrapper

    return decorator
