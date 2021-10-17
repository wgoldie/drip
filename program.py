from dataclasses import dataclass, field
import typing
import ops
import drip_ast as ast

@dataclass(frozen=True)
class Subroutine:
    ops: typing.Tuple[ops.ByteCodeOp, ...]
    arguments: typing.Tuple[str, ...]

@dataclass(frozen=True)
class Program:
    subroutines: typing.Dict[str, Subroutine]
    structures: typing.Dict[str, ast.StructureDefinition] = field(default_factory=dict)
