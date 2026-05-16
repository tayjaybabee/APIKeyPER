from typing import Callable
from argparse import Namespace


COMMAND_HANDLERS: dict[str, Callable[[Namespace], int]] = {}


def register(command: str):

    def decco(fn: Callable[[Namespace], int]):
        COMMAND_HANDLERS[command] = fn
        return fn

    return decco
