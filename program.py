from dataclasses import dataclass
import typing
import ops

@dataclass(frozen=True)
class Subroutine:
    ops: typing.Tuple[ops.ByteCodeOp, ...]
    arguments: typing.Tuple[str]

@dataclass(frozen=True)
class Program:
    subroutines: typing.Dict[str, Subroutine]
