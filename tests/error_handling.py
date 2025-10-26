import oven


@oven.monitor
def err_func():
    raise ValueError("Test error")

if __name__ == "__main__":
    err_func()