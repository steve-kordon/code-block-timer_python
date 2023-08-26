from __future__ import annotations

import threading
import time


def get() -> CodeBlockTimer:
    """
    This method gets the local code block timer.

    Returns:
        The local code block timer.
    """
    thread_local_data = threading.local()
    if not hasattr(thread_local_data, "code_block_timer"):
        thread_local_data.code_block_timer = CodeBlockTimer()

    return thread_local_data.code_block_timer


class CodeBlockTimer:
    """
    The code block timer
    """

    instances: list[_CodeBlockTimerInstance]
    active_instance: _CodeBlockTimerInstance

    def __init__(self):
        """
        Creates a new code block timer.
        """
        self.instances = list()

    def start(self, name: str) -> CodeBlockTimerCloseable:
        """
        Starts a new code block timer.

        Args:
            name: The name of the code block timer.

        Returns:
            The code block timer closeable.
        """
        instance = _CodeBlockTimerInstance(name, self.active_instance)

        if self.active_instance is None:
            self.instances.append(instance)

        self.active_instance = instance

        return CodeBlockTimerCloseable(self, name)

    def stop(self, name: str) -> None:
        """
        Stops a code block timer.
        Args:
            name: The name of the code block timer instance.
        """
        if self.active_instance is None:
            return

        if self.active_instance.name != name:
            raise ValueError("Cannot stop a timer that is not the active one.")

        self.active_instance = self.active_instance.stop()

    def add_sub_timer(self, sub_code_block_timer: CodeBlockTimer) -> None:
        """
        Adds a sub code block timer.
        This is used when adding the timer of a child thread.

        Add at the end of the sub timer's life, or the
        instances will be missed.

        Args:
            sub_code_block_timer: The sub code block timer.
        """
        if self.active_instance is None:
            self.instances.extend(sub_code_block_timer.instances)
            return

        for sub_timer_instance in sub_code_block_timer.instances:
            self.active_instance.add_child_instance(sub_timer_instance)

    def print(self) -> None:
        """
        Prints the code block timings.
        """
        print(self.to_string())

    def to_string(self) -> str:
        """
        Returns the code block timings as a string.

        Returns:
            The code block timings as a string.
        """

        self_string = ""

        for instance in self.instances:
            self_string += instance.to_string(0)

        return self_string


class CodeBlockTimerCloseable:
    """
    The code block timer closeable.
    """

    code_block_timer: CodeBlockTimer
    instance_name: str

    def __init__(self, code_block_timer: CodeBlockTimer, instance_name: str):
        """
        Initializes a new instance of the code block timer closeable class.

        Args:
            code_block_timer: The code block timer.
            instance_name: The instance name.
        """
        self.code_block_timer = code_block_timer
        self.instance_name = instance_name

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exits the code block timer closeable.

        Args:
            exc_type: any
            exc_value: any
            traceback: any
        """
        self.code_block_timer.stop(self.instance_name)


class _CodeBlockTimerInstance:
    """
    The code block timer instance.
    """

    __INDENT_SIZE: int = 2

    name: str
    start_time: int
    stop_time: int
    parent_instance: _CodeBlockTimerInstance
    child_instances: list[_CodeBlockTimerInstance]

    def __init__(self, name: str, parent_instance: _CodeBlockTimerInstance):
        """
        Initializes a new instance of the code block timer instance class.

        Args:
            name: The name.
            parent_instance: The parent instance.
        """
        self.name = name
        self.parent_instance = parent_instance

        if self.parent_instance is not None:
            self.parent_instance.child_instances.append(self)

        self.start_time = round(time.time() * 1000.0)

    def stop(self) -> _CodeBlockTimerInstance:
        """
        Stops the code block timer instance.

        Returns:
            The parent instance.
        """
        self.stop_time = round(time.time() * 1000.0)

        return self.parent_instance

    def get_duration(self) -> int:
        """
        Gets the duration.

        Returns:
            The duration.
        """
        return self.stop_time - self.start_time

    def add_child_instance(self, child: _CodeBlockTimerInstance) -> None:
        """
        Adds a child.

        Args:
            child: The child.
        """
        if self.child_instances is None:
            self.child_instances = list()

        self.child_instances.append(child)

    def to_string(self, indent: int) -> str:
        """
        Returns the code block timer instance as a string.

        Args:
            indent: The indent.

        Returns:
            The code block timer instance as a string.
        """
        self_string = ""
        if indent > 0:
            self_string += " " * (indent * self.__INDENT_SIZE)

        self_string += f"{self.name}: {self.get_duration()}\n"

        if self.child_instances is None:
            return self_string

        for child_instance in self.child_instances:
            self_string += child_instance.to_string(indent + 1)

        return self_string
