import threading
import time

import project.code_block_timer as cbt


def test() -> None:
    """
    Test that the code block timer runs without errors.
    """

    timer = cbt.get()

    with timer.start("test1"):
        _waste_time()
        timer.start("test2")
        _waste_time()
        timer.stop("test2")

    timer.start("test3")

    thread = threading.Thread(target=_sub_thread, args=(timer,))
    thread.start()
    thread.join()

    timer.stop("test3")

    timer.print()


def _waste_time() -> None:
    """
    This function is used to simulate a waste of time.
    """
    time.sleep(1)


def _sub_thread(parent_timer: cbt.CodeBlockTimer) -> None:
    """
    This function is used to simulate a sub thread.
    """
    sub_timer = cbt.get()

    with sub_timer.start("test4"):
        _waste_time()

    parent_timer.add_sub_timer(sub_timer)


if __name__ == "__main__":
    test()
