from dataclasses import dataclass, field, replace
from functools import cached_property
import drip.typecheck as drip_typing
from drip.typecheck import StructureDefinition, ArgumentDefinition
import typing
import enum
import abc


@dataclass(frozen=True, eq=True)
class NamedStructureDefinition:
    structure: drip_typing.StructureDefinition
    name: str


@dataclass(frozen=True, eq=True)
class TypeCheckingContext:
    structure_lookup: typing.Dict[str, StructureDefinition] = field(
        default_factory=dict
    )
    function_return_types: typing.Dict[str, drip_typing.ExpressionType] = field(
        default_factory=dict
    )
    local_scope: typing.Dict[str, drip_typing.ExpressionType] = field(
        default_factory=dict
    )


def primitive_name_to_type(primitive_name: str) -> drip_typing.ConcreteType:
    return drip_typing.ConcreteType(
        type=drip_typing.PrimitiveType(drip_typing.PRIMITIVES[primitive_name])
    )


def type_name_to_type(
    context: TypeCheckingContext, type_name: str
) -> drip_typing.ExpressionType:
    if type_name in drip_typing.PRIMITIVES:
        return primitive_name_to_type(type_name)
    elif type_name in context.structure_lookup:
        return drip_typing.ConcreteType(
            type=drip_typing.StructureType(
                structure=context.structure_lookup[type_name]
            )
        )
    else:
        raise ValueError("Unknown type", type_name)


class Expression(abc.ABC):
    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        ...


@dataclass(frozen=True, eq=True)
class LiteralExpression(Expression):
    type_name: str
    value: float

    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        return primitive_name_to_type(self.type_name)


@dataclass(frozen=True, eq=True)
class VariableReferenceExpression(Expression):
    name: str

    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        return context.local_scope[self.name]


@dataclass(frozen=True, eq=True)
class ConstructionExpression(Expression):
    type_name: str
    arguments: typing.Dict[str, "Expression"]
    type_arguments: typing.Dict[str, str] = field(default_factory=dict)

    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        structure = context.structure_lookup[self.type_name]
        if len(self.type_arguments) == 0:
            return drip_typing.ConcreteType(
                type=drip_typing.StructureType(structure=structure)
            )
        else:
            return drip_typing.ConcreteType(
                type=drip_typing.StructureType(
                    structure=structure.resolve_type(
                        {
                            argument_name: type_name_to_type(context, argument_type)
                            for argument_name, argument_type in self.type_arguments.items()
                        }
                    )
                )
            )


@dataclass(frozen=True, eq=True)
class FunctionCallExpression(Expression):
    function_name: str
    arguments: typing.Dict[str, "Expression"]

    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        return context.function_return_types[self.function_name]


@dataclass(frozen=True, eq=True)
class PropertyAccessExpression(Expression):
    entity: "Expression"
    property_name: str

    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        entity_type = self.entity.type_check(context)

        assert isinstance(entity_type, drip_typing.ConcreteType)
        assert isinstance(entity_type.type, drip_typing.StructureType)
        field = entity_type.type.structure.field_lookup[self.property_name]
        return field.type


class BinaryOperator(enum.Enum):
    ADD = enum.auto()
    SUBTRACT = enum.auto()


@dataclass(frozen=True, eq=True)
class BinaryOperatorExpression(Expression):
    operator: BinaryOperator
    lhs: "Expression"
    rhs: "Expression"

    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        lhs_type = self.lhs.type_check(context)
        rhs_type = self.rhs.type_check(context)
        assert lhs_type == rhs_type
        return lhs_type


@dataclass(frozen=True, eq=True)
class ReturnStatement:
    expression: "Expression"


@dataclass(frozen=True, eq=True)
class AssignmentStatement:
    variable_name: str
    expression: Expression


Statement = typing.Union[AssignmentStatement, ReturnStatement]


@dataclass(frozen=True, eq=True)
class FunctionDefinition:
    name: str
    arguments: typing.Tuple[drip_typing.ArgumentDefinition, ...]
    procedure: typing.Tuple[Statement, ...]

    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        context = replace(
            context,
            local_scope={argument.name: argument.type for argument in self.arguments},
        )
        return_set = False
        return_type = None
        for statement in self.procedure:
            if return_set:
                raise ValueError("Code after return")

            if isinstance(statement, ReturnStatement):
                return_type = statement.expression.type_check(context)
                return_set = True
            elif isinstance(statement, AssignmentStatement):
                statement_expression_type = statement.expression.type_check(context)
                assert (
                    statement.variable_name not in context.local_scope
                    or statement_expression_type
                    == context.local_scope[statement.variable_name]
                )
                context = replace(
                    context,
                    local_scope={
                        **context.local_scope,
                        statement.variable_name: statement_expression_type,
                    },
                )
            else:
                raise NotImplementedError(type(statement))
        assert return_type is not None
        return return_type


@dataclass(frozen=True, eq=True)
class Program:
    structure_definitions: typing.Tuple[NamedStructureDefinition, ...] = tuple()
    function_definitions: typing.Tuple[FunctionDefinition, ...] = tuple()

    @cached_property
    def structure_lookup(self) -> typing.Dict[str, drip_typing.StructureDefinition]:
        return {
            structure_definition.name: structure_definition.structure
            for structure_definition in self.structure_definitions
        }

    @cached_property
    def function_lookup(self) -> typing.Dict[str, FunctionDefinition]:
        return {
            function_definition.name: function_definition
            for function_definition in self.function_definitions
        }

    def type_check(self) -> TypeCheckingContext:
        context = TypeCheckingContext(structure_lookup=self.structure_lookup)
        for function_definition in self.function_definitions:
            function_type = function_definition.type_check(context)
            context = replace(
                context,
                function_return_types={
                    **context.function_return_types,
                    function_definition.name: function_type,
                },
            )
        return context


@dataclass(frozen=True, eq=True)
class FinalizationContext:
    type_parameters: typing.Tuple[str]


def resolve_preliminary_type_name(
    context: FinalizationContext, type_name: str
) -> drip_typing.ExpressionType:
    pass


@dataclass(frozen=True, eq=True)
class ArgumentDefinitionPreliminary:
    name: str
    type_name: str


@dataclass(frozen=True, eq=True)
class StructureDefinitionPreliminary:
    name: str
    fields: typing.Tuple[ArgumentDefinitionPreliminary, ...]
    type_parameters: typing.Tuple[str, ...] = tuple()


@dataclass(frozen=True, eq=True)
class FunctionDefinitionPreliminary:
    name: str
    arguments: typing.Tuple[ArgumentDefinitionPreliminary, ...]
    procedure: typing.Tuple[Statement, ...]


def finalize_arguments(
    context: TypeCheckingContext,
    arguments: typing.Tuple[ArgumentDefinitionPreliminary, ...],
) -> typing.Tuple[ArgumentDefinition, ...]:
    return tuple(
        ArgumentDefinition(
            name=argument.name, type=type_name_to_type(context, argument.type_name)
        )
        for argument in arguments
    )


@dataclass(frozen=True, eq=True)
class ProgramPreliminary:
    structure_definitions: typing.Tuple[StructureDefinitionPreliminary, ...] = tuple()
    function_definitions: typing.Tuple[FunctionDefinitionPreliminary, ...] = tuple()

    def finalize(self) -> Program:
        structure_lookup: typing.Dict[str, StructureDefinition] = {}
        for definition in self.structure_definitions:
            structure_lookup[definition.name] = drip_typing.StructureDefinition(
                type_parameters=definition.type_parameters,
                fields=finalize_arguments(
                    TypeCheckingContext(structure_lookup=structure_lookup),
                    definition.fields,
                ),
            )
        final_context = TypeCheckingContext(structure_lookup=structure_lookup)
        return Program(
            structure_definitions=tuple(
                NamedStructureDefinition(name=name, structure=structure)
                for name, structure in structure_lookup.items()
            ),
            function_definitions=tuple(
                FunctionDefinition(
                    name=definition.name,
                    arguments=finalize_arguments(final_context, definition.arguments),
                    procedure=definition.procedure,
                )
                for definition in self.function_definitions
            ),
        )
