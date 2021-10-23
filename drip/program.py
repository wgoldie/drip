from dataclasses import field
import typing
from drip.validated_dataclass import validated_dataclass
import drip.ops as ops
import drip.ast as ast


@validated_dataclass
class Subroutine:
    ops: typing.Tuple[ops.ByteCodeOp, ...]
    arguments: typing.Tuple[str, ...]


@validated_dataclass
class Program:
    subroutines: typing.Dict[str, Subroutine]
    structures: typing.Dict[str, ast.StructureDefinition] = field(default_factory=dict)
