import time
import subprocess

import oven


@oven.monitor
def test_bake_wrapper() -> None:
    print('Test function wrapper `@oven.bake`.')
    time.sleep(1)


def test_ding_func() -> None:
    print('Test function `oven.ding`.')
    msg = '[test_ding_func] Hello World!'
    oven.notify(msg)


def test_bake_cli() -> None:
    print('Test CLI command `bake`.')
    cmd = 'bake echo "[test_bake_cli] Hello World!"'
    subprocess.run(cmd, shell=True, check=True, encoding='utf-8')


def test_ding_cli() -> None:
    print('Test CLI command `ding`.')
    cmd = 'ding "[test_ding_cli] Hello World!"'
    subprocess.run(cmd, shell=True, check=True, encoding='utf-8')


if __name__ == '__main__':
    test_bake_wrapper()
    input('Press Enter to continue...')
    test_ding_func()
    input('Press Enter to continue...')
    test_bake_cli()
    input('Press Enter to continue...')
    test_ding_cli()
