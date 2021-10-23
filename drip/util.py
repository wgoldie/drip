import typing
from drip.basetypes import Stack, StackValue
from drip.validated_dataclass import validated_dataclass


@validated_dataclass
class PopN:
    stack: Stack
    values: Stack


def pop_n(stack: typing.Tuple[StackValue, ...], n: int) -> PopN:
    assert n >= 0
    assert len(stack) >= n
    return PopN(stack=stack[:-n], values=stack[-n:])


@validated_dataclass
class Pop:
    stack: Stack
    value: StackValue


def pop(stack: Stack) -> Pop:
    popped = pop_n(stack, n=1)
    return Pop(stack=popped.stack, value=popped.values[0])
