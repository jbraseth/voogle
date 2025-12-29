# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""Utilities for polling and waiting for conditions in tests."""

import logging
import time
from typing import Callable, Optional, Union

from e2e.shared.readable_time import get_readable_seconds

# Use WaitUntil or the convenience function wait_until to wait for a condition to be True.
# In most cases, use the wait_until convenience function declared at the end of this file
#
# For example:
# def check_condition():
#    return True if <x> else False
#
# wait_until(f, max_seconds=10, poll_interval=1)
#      If label is not specified, the label is the function name, unless it's a partial function, then "Wait Until" is the label.
#      The function f should return True when the condiction is satisfied, otherwise return False.
#      If the function f throws an exception, the exception is not caught, so when used in a pytest,
#      it has the same effect as an assertion.


class WaitUntil:
    ENABLE_LOGGING = True

    def __init__(self, label: str, max_seconds: float = 1.0, poll_interval: Union[float, list[float]] = 0.1,
                 positive_desc="condition met", negative_desc="condition not met", enable_logging=True):
        self.__label = label
        self.__poll_interval = poll_interval
        self.__max_seconds = max_seconds
        self.__positive_desc = positive_desc
        self.__negative_desc = negative_desc
        self.__enable_logging = enable_logging and WaitUntil.ENABLE_LOGGING

    def set_label(self, label: str) -> None:
        self.__label = label

    def set_max_seconds(self, max_seconds: float) -> None:
        self.__max_seconds = max_seconds

    def set_poll_interval(self, poll_interval: Union[float, list[float]]) -> None:
        self.__poll_interval = poll_interval

    def set_enable_logging(self, enable_logging) -> None:
        self.__enable_logging = enable_logging

    def wait_until(self, check: Callable[[], bool], max_seconds=None, poll_interval=None, positive_desc=None, negative_desc=None) -> bool:
        if max_seconds is not None:
            self.__max_seconds = max_seconds
        if poll_interval is not None:
            self.__poll_interval = poll_interval
        if positive_desc is not None:
            self.__positive_desc = positive_desc
        if negative_desc is not None:
            self.__negative_desc = negative_desc

        start = None if self.__max_seconds == 0.0 else time.time()
        elapsed = 0
        poll_index = 0
        while True:
            if check():
                if start is not None:
                    if self.__enable_logging:
                        logging.info("[%s] %s after %s.", self.__label, self.__positive_desc,
                                     get_readable_seconds(time.time() - start))
                return True
            if start is None or (elapsed > self.__max_seconds):
                break
            poll_index = self.__sleep(poll_index, elapsed)
            elapsed = time.time() - start
            if self.__enable_logging:
                logging.info("[%s] %s elapsed (max timeout is %s).", self.__label,
                             get_readable_seconds(elapsed),
                             get_readable_seconds(self.__max_seconds))

        if self.__enable_logging:
            logging.warning("[%s] %s after %s.", self.__label, self.__negative_desc,
                            get_readable_seconds(time.time() - start if start is not None else 0))
        return False

    def wait_until_running(self, check: Callable[[], bool]) -> bool:
        '''convenience function'''
        return self.wait_until(check, positive_desc="Running", negative_desc="Not running")

    def wait_until_stopped(self, check: Callable[[], bool]) -> bool:
        '''convenience function'''
        return self.wait_until(check, positive_desc="Stopped", negative_desc="Not stopping")

    def __sleep(self, poll_index, elapsed: float) -> int:
        """poll interval can be a list of numbers or a number representing seconds"""
        interval = 1
        next_poll_index = 0
        if type(self.__poll_interval) is float or type(self.__poll_interval) is int:
            interval = self.__poll_interval
        elif type(self.__poll_interval) is list and len(self.__poll_interval) > 0:
            interval = self.__poll_interval[poll_index] if poll_index < len(self.__poll_interval) else self.__poll_interval[-1]
            next_poll_index = poll_index + 1

        if interval > self.__max_seconds - elapsed:
            interval = self.__max_seconds - elapsed
        if interval <= 0:
            interval = 0.1
        time.sleep(interval)
        return next_poll_index


# convenience function to create WaitUnit and call wait_until member function
def wait_until(f: Callable[[], bool],
               label: Optional[str] = None,
               max_seconds: float = 1.0,
               poll_interval: Union[float, list[float]] = 0.1,
               positive_desc: str = "condition met",
               negative_desc: str = "condition not met",
               enable_logging: bool = True) -> bool:
    resolved_label = label if label is not None else getattr(f, "__name__", "Wait Until")
    checker = WaitUntil(resolved_label,
                        max_seconds=max_seconds,
                        poll_interval=poll_interval,
                        positive_desc=positive_desc,
                        negative_desc=negative_desc,
                        enable_logging=enable_logging)
    return checker.wait_until(f)
