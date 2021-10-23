from __future__ import annotations
import typing
from functools import cached_property
from dataclasses import replace
from drip.validated_dataclass import validated_dataclass
import abc


@validated_dataclass
class Placeholder:
    name: str


@validated_dataclass
class ArgumentDefinition:
    name: str
    type: ExpressionType


@validated_dataclass
class StructureDefinition:
    fields: typing.Tuple[ArgumentDefinition, ...]
    type_parameters: typing.Tuple[str, ...] = tuple()

    @cached_property
    def field_lookup(self) -> typing.Dict[str, ArgumentDefinition]:
        return {field.name: field for field in self.fields}

    def resolve_type(
        self, parameter_types: typing.Dict[str, ExpressionType]
    ) -> "StructureDefinition":
        if len(self.type_parameters) == 0:
            return self

        return replace(
            self,
            type_parameters=tuple(),
            fields=tuple(
                replace(field, type=parameter_types[field.type.name])
                if isinstance(field.type, Placeholder)
                else field
                for field in self.fields
            ),
        )


@validated_dataclass
class StructureType:
    structure: StructureDefinition


@validated_dataclass
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


@validated_dataclass
class ConcreteType:
    type: DripType


@validated_dataclass
class TypeParameter:
    name: str


"""
@validated_dataclass
class ParameterizedType(abc.ABC):
    def yield_type(
        self, parameter_types: typing.Dict[str, ExpressionType]
    ) -> DripType:
        ...
"""


ExpressionType = typing.Union[ConcreteType, Placeholder]
