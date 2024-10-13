import time


def timer(*, switch: bool = True) -> callable:
    if switch:
        def wrapperFur1(func):
            def wrapper1(self, *args, **kwargs):
                start_time = time.time()
                result = func(self, *args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                print(f"{func.__name__} 运行时间为 {execution_time:.6f} 秒")
                return result  # 返回函数的结果

            return wrapper1

        return wrapperFur1
    else:
        def wrapperFur2(func):
            def wrapper2(self, *args, **kwargs):
                result = func(self, *args, **kwargs)
                return result  # 返回函数的结果

            return wrapper2

        return wrapperFur2


def progress(func):
    def wrapper(self, *args, **kwargs):
        for number in range(cut := 10):
            pro_g = "#" * number + "-" * (number - (cut + 1))
            print(f"\r\033[1:32m[:{pro_g}:]", end="")
            func(self, *args, **kwargs)
        return

    return wrapper


def catchError(func) -> callable:
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(f"函数抛出{e}")
        return func

    return wrapper


if __name__ == '__main__':
    pass
