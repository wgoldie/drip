import typing
from functools import cached_property
from dataclasses import dataclass, replace
import abc


@dataclass(frozen=True, eq=True)
class Placeholder:
    name: str


@dataclass(frozen=True, eq=True)
class ArgumentDefinition:
    name: str
    type: "ExpressionType"


@dataclass(frozen=True, eq=True)
class StructureDefinition:
    fields: typing.Tuple[ArgumentDefinition, ...]
    type_parameters: typing.Tuple[str, ...] = tuple()

    @cached_property
    def field_lookup(self) -> typing.Dict[str, ArgumentDefinition]:
        return {field.name: field for field in self.fields}

    def resolve_type(
        self, parameter_types: typing.Dict[str, "ExpressionType"]
    ) -> "StructureDefinition":
        if len(self.type_parameters) == 0:
            return self

        return replace(
            self,
            fields=tuple(
                replace(field, type=parameter_types[field.type.name])
                if isinstance(field.type, Placeholder)
                else field
                for field in self.fields
            ),
        )


@dataclass(frozen=True, eq=True)
class StructureType:
    structure: StructureDefinition


@dataclass(frozen=True, eq=True)
class PrimitiveType:
    primitive: typing.Union[
        typing.Type[int],
        typing.Type[float],
    ]


PRIMITIVES = {
    "Int": int,
    "Float": float,
}

DripType = typing.Union[
    PrimitiveType,
    StructureType,
]


@dataclass(frozen=True, eq=True)
class ConcreteType:
    type: DripType


@dataclass(frozen=True, eq=True)
class TypeParameter:
    name: str


"""
@dataclass(frozen=True, eq=True)
class ParameterizedType(abc.ABC):
    def yield_type(
        self, parameter_types: typing.Dict[str, "ExpressionType"]
    ) -> DripType:
        ...
"""


ExpressionType = typing.Union[ConcreteType, Placeholder]
