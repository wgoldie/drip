from dataclasses import dataclass, field
from functools import cached_property
import drip.typecheck as drip_typing
import typing
import enum
import abc

@dataclass(frozen=True, eq=True)
class TypeCheckingContext:
    program: 'Program'
    function_name: str
    function_return_types: typing.Dict[str, drip_typing.ExpressionType] = field(default_factory=dict)
    local_scope: typing.Dict[str, drip_typing.ExpressionType] = field(default_factory=dict)

class Expression(abc.ABC):
    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        ...

@dataclass(frozen=True)
class LiteralExpression(Expression):
    value: float

    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        return drip_typing.ConcreteType(type=drip_typing.PrimitiveType(primitive=float))


@dataclass(frozen=True)
class VariableReferenceExpression(Expression):
    name: str

    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        return context.local_scope[self.name]


@dataclass(frozen=True)
class ConstructionExpression(Expression):
    type_name: str
    arguments: typing.Dict[str, "Expression"]

    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        assert self.type_name in context.program.structure_lookup
        return drip_typing.ConcreteType(type=drip_typing.StructureType(structure_name=self.type_name))


@dataclass(frozen=True)
class FunctionCallExpression(Expression):
    function_name: str
    arguments: typing.Dict[str, "Expression"]

    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        return context.function_return_types[self.function_name]

def type_name_to_type(context: TypeCheckingContext, type_name: str) -> drip_typing.ExpressionType:
    if type_name in drip_typing.PRIMITIVES:
        return drip_typing.ConcreteType(
            type=drip_typing.PrimitiveType(
                drip_typing.PRIMITIVES[type_name]))
    elif type_name in context.program.structure_lookup:
        return drip_typing.ConcreteType(
            type=drip_typing.StructureType(
                structure_name=type_name))
    else:
        raise ValueError("Unknown type", type_name)

@dataclass(frozen=True)
class PropertyAccessExpression(Expression):
    entity: "Expression"
    property_name: str

    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        entity_type = self.entity.type_check(context)

        assert isinstance(entity_type, drip_typing.ConcreteType)
        assert isinstance(entity_type.type, drip_typing.StructureType)
        structure = context.program.structure_lookup[entity_type.type.structure_name]
        field = structure.field_lookup[self.property_name]
        return type_name_to_type(context, field.type_name)


class BinaryOperator(enum.Enum):
    ADD = enum.auto()
    SUBTRACT = enum.auto()


@dataclass(frozen=True)
class BinaryOperatorExpression(Expression):
    operator: BinaryOperator
    lhs: "Expression"
    rhs: "Expression"

    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        lhs_type = self.lhs.type_check(context)
        rhs_type = self.rhs.type_check(context)
        assert lhs_type == rhs_type
        return lhs_type


@dataclass(frozen=True)
class ReturnStatement:
    expression: "Expression"


@dataclass(frozen=True)
class AssignmentStatement:
    variable_name: str
    expression: Expression


Statement = typing.Union[AssignmentStatement, ReturnStatement]


@dataclass(frozen=True)
class ArgumentDefinition:
    name: str
    type_name: str


@dataclass(frozen=True)
class FunctionDefinition:
    name: str
    arguments: typing.Tuple[ArgumentDefinition, ...]
    procedure: typing.Tuple[Statement, ...]


@dataclass(frozen=True)
class StructureDefinition:
    name: str
    fields: typing.Tuple[ArgumentDefinition, ...]

    @cached_property
    def field_lookup(self) -> typing.Dict[str, ArgumentDefinition]:
        return {
            field.name: field
            for field in self.fields
        }


@dataclass(frozen=True)
class Program:
    structure_definitions: typing.Tuple[StructureDefinition, ...] = tuple()
    function_definitions: typing.Tuple[FunctionDefinition, ...] = tuple()

    @cached_property
    def structure_lookup(self) -> typing.Dict[str, StructureDefinition]:
        return {
            structure_definition.name: structure_definition
            for structure_definition in self.structure_definitions
        }

    @cached_property
    def function_lookup(self) -> typing.Dict[str, FunctionDefinition]:
        return {
            function_definition.name: function_definition
            for function_definition in self.function_definitions
        }
