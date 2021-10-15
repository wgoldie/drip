from dataclasses import dataclass
import typing
import ops

@dataclass(frozen=True)
class Program:
    subroutines: typing.Dict[str, typing.Tuple[ops.ByteCodeOp, ...]]
