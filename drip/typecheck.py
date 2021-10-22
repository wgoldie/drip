import typing
from dataclasses import dataclass

@dataclass(frozen=True, eq=True)
class StructureType:
    structure_name: str

@dataclass(frozen=True, eq=True)
class PrimitiveType:
    primitive: typing.Union[
        typing.Type[int],
        typing.Type[float],
    ]

PRIMITIVES = {
    'int': int,
    'float': float,
}

DripType = typing.Union[
    PrimitiveType,
    StructureType,
]

@dataclass(frozen=True, eq=True)
class ConcreteType:
    type: DripType

ExpressionType = typing.Union[ConcreteType]

