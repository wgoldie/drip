import typing
from dataclasses import dataclass, field

T = typing.TypeVar('T')

@dataclass
class TaggedValue(typing.Generic[T]):
    tag: typing.Type[T]
    value: T


StackValue = typing.Union[TaggedValue[int]]
Stack = typing.Tuple[StackValue, ...]
OpArg = typing.Union[StackValue]
Name = str

@dataclass(frozen=True)
class ProgramState:
    stack: Stack = field(default_factory=tuple)
    names: typing.Dict[Name, StackValue] = field(default_factory=dict)
    return_value: typing.Optional[int] = None
    flags: typing.Dict[Name, int] = field(default_factory=dict)
    program_counter: int = 0
