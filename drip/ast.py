from dataclasses import dataclass
import typing
import enum

@dataclass(frozen=True)
class LiteralExpression:
    value: float

@dataclass(frozen=True)
class VariableReferenceExpression:
    name: str

@dataclass(frozen=True)
class ConstructionExpression:
    type_name: str
    arguments: typing.Dict[str, 'Expression']

@dataclass(frozen=True)
class FunctionCallExpression:
    function_name: str
    arguments: typing.Dict[str, 'Expression']

@dataclass(frozen=True)
class PropertyAccessExpression:
    entity: 'Expression'
    property_name: str

class BinaryOperator(enum.Enum):
    ADD = enum.auto()
    SUBTRACT = enum.auto()

@dataclass(frozen=True)
class BinaryOperatorExpression:
    operator: BinaryOperator
    lhs: 'Expression'
    rhs: 'Expression'

Expression = typing.Union[
    ConstructionExpression,
    VariableReferenceExpression,
    LiteralExpression,
    PropertyAccessExpression,
    BinaryOperatorExpression]

@dataclass(frozen=True)
class ReturnStatement:
    expression: 'Expression'

@dataclass(frozen=True)
class AssignmentStatement:
    variable_name: str
    expression: Expression

Statement = typing.Union[AssignmentStatement, ReturnStatement]

@dataclass(frozen=True)
class FunctionDefinition:
    name: str
    arguments: typing.Dict[str, str]
    procedure: typing.Tuple[Statement, ...]

@dataclass(frozen=True)
class StructureFieldDefinition:
    name: str
    type_name: str

@dataclass(frozen=True)
class StructureDefinition:
    name: str
    fields: typing.Tuple[StructureFieldDefinition, ...]


@dataclass(frozen=True)
class Program:
    structure_definitions: typing.Tuple[StructureDefinition, ...]
    function_definitions: typing.Tuple[FunctionDefinition, ...]
