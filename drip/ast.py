from dataclasses import dataclass, field, replace
from drip.validated_dataclass import validated_dataclass
from functools import cached_property
from drip.constants import INDENT
import drip.typecheck as drip_typing
from drip.typecheck import StructureDefinition, ArgumentDefinition
import typing
import enum
import abc


@validated_dataclass
class NamedStructureDefinition:
    structure: drip_typing.StructureDefinition
    name: str

    def serialize(self) -> str:
        return self.structure.serialize(name=self.name)


@validated_dataclass
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
        type=drip_typing.PrimitiveType(primitive=drip_typing.PRIMITIVES[primitive_name])
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
    @abc.abstractmethod
    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        ...

    @abc.abstractmethod
    def serialize(self) -> str:
        ...


@validated_dataclass
class LiteralExpression(Expression):
    type_name: str
    value: float

    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        return primitive_name_to_type(self.type_name)

    def serialize(self) -> str:
        return str(self.value)


@validated_dataclass
class VariableReferenceExpression(Expression):
    name: str

    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        return context.local_scope[self.name]

    def serialize(self) -> str:
        return self.name


@validated_dataclass
class ConstructionExpression(Expression):
    type_name: str
    arguments: typing.Dict[str, Expression]
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

    def serialize(self) -> str:
        argument_parts = [
            f"{argument_name}={expression.serialize()}"
            for argument_name, expression in self.arguments.items()
        ]
        type_argument_parts = [
            f"{argument_name}={type_name}"
            for argument_name, type_name in self.type_arguments.items()
        ]
        type_parameters_snippet = (
            f" [', '.join(type_argument_parts)]" if len(type_argument_parts) > 0 else ""
        )
        return (
            f"{self.type_name}{type_parameters_snippet} ({', '.join(argument_parts)})"
        )


@validated_dataclass
class FunctionCallExpression(Expression):
    function_name: str
    arguments: typing.Dict[str, Expression]

    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        return context.function_return_types[self.function_name]

    def serialize(self) -> str:
        argument_parts = [
            f"{argument_name}={expression.serialize()}"
            for argument_name, expression in self.arguments.items()
        ]
        return f"{self.function_name}({', '.join(argument_parts)})"


@validated_dataclass
class PropertyAccessExpression(Expression):
    entity: Expression
    property_name: str

    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        entity_type = self.entity.type_check(context)

        assert isinstance(entity_type, drip_typing.ConcreteType)
        assert isinstance(entity_type.type, drip_typing.StructureType)
        field = entity_type.type.structure.field_lookup[self.property_name]
        return field.type

    def serialize(self) -> str:
        return f"{self.entity.serialize()}.{self.property_name}"


class BinaryOperator(str, enum.Enum):
    ADD = "+"
    SUBTRACT = "-"


@validated_dataclass
class BinaryOperatorExpression(Expression):
    operator: BinaryOperator
    lhs: Expression
    rhs: Expression

    def type_check(self, context: TypeCheckingContext) -> drip_typing.ExpressionType:
        lhs_type = self.lhs.type_check(context)
        rhs_type = self.rhs.type_check(context)
        assert lhs_type == rhs_type
        return lhs_type

    def serialize(self) -> str:
        return f"({self.lhs.serialize()} {self.operator.value} {self.rhs.serialize()})"


@validated_dataclass
class ReturnStatement:
    expression: Expression

    def serialize(self) -> str:
        return f"return {self.expression.serialize()}"


@validated_dataclass
class AssignmentStatement:
    variable_name: str
    expression: Expression

    def serialize(self) -> str:
        return f"{self.variable_name} = {self.expression.serialize()}"


Statement = typing.Union[AssignmentStatement, ReturnStatement]


@validated_dataclass
class FunctionDefinition:
    name: str
    arguments: typing.Tuple[drip_typing.ArgumentDefinition, ...]
    procedure: typing.Tuple[Statement, ...]
    return_type: drip_typing.ExpressionType
    return_type_name: str

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
        assert return_type == self.return_type
        return return_type

    def serialize(self) -> str:
        return (
            f"function {self.name} ("
            + "".join(
                [f"\n{INDENT}{argument.serialize()}," for argument in self.arguments]
            )
            + f"\n) -> {self.return_type_name} ("
            + "".join(
                [f"\n{INDENT}{statement.serialize()};" for statement in self.procedure]
            )
            + "\n)"
        )


@validated_dataclass
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

    def serialize(self) -> str:
        snippets = []
        for structure_definition in self.structure_definitions:
            snippets.append(structure_definition.serialize())

        for function_definition in self.function_definitions:
            snippets.append(function_definition.serialize())
        return "\n\n".join(snippets)


@validated_dataclass
class ArgumentDefinitionPreliminary:
    name: str
    type_name: str


@validated_dataclass
class StructureDefinitionPreliminary:
    name: str
    fields: typing.Tuple[ArgumentDefinitionPreliminary, ...] = tuple()
    type_parameters: typing.Tuple[str, ...] = tuple()


@validated_dataclass
class FunctionDefinitionPreliminary:
    name: str
    return_type_name: str
    arguments: typing.Tuple[ArgumentDefinitionPreliminary, ...] = tuple()
    procedure: typing.Tuple[Statement, ...] = tuple()

    def finalize(self, context: TypeCheckingContext) -> FunctionDefinition:
        return FunctionDefinition(
            name=self.name,
            arguments=finalize_arguments(
                context=context,
                type_parameters=tuple(),
                arguments=self.arguments,
            ),
            return_type_name=self.return_type_name,
            return_type=type_name_to_type(context, self.return_type_name),
            procedure=self.procedure,
        )


def finalize_arguments(
    context: TypeCheckingContext,
    type_parameters: typing.Tuple[str, ...],
    arguments: typing.Tuple[ArgumentDefinitionPreliminary, ...],
) -> typing.Tuple[ArgumentDefinition, ...]:
    return tuple(
        ArgumentDefinition(
            name=argument.name,
            type=type_name_to_type(context, argument.type_name)
            if argument.type_name not in type_parameters
            else drip_typing.Placeholder(name=argument.type_name),
            type_name=argument.type_name,
        )
        for argument in arguments
    )


@validated_dataclass
class ProgramPreliminary:
    structure_definitions: typing.Tuple[StructureDefinitionPreliminary, ...] = tuple()
    function_definitions: typing.Tuple[FunctionDefinitionPreliminary, ...] = tuple()

    def finalize(self) -> Program:
        structure_lookup: typing.Dict[str, StructureDefinition] = {}
        for definition in self.structure_definitions:
            structure_lookup[definition.name] = drip_typing.StructureDefinition(
                type_parameters=definition.type_parameters,
                fields=finalize_arguments(
                    context=TypeCheckingContext(structure_lookup=structure_lookup),
                    type_parameters=definition.type_parameters,
                    arguments=definition.fields,
                ),
            )
        final_context = TypeCheckingContext(structure_lookup=structure_lookup)
        return Program(
            structure_definitions=tuple(
                NamedStructureDefinition(name=name, structure=structure)
                for name, structure in structure_lookup.items()
            ),
            function_definitions=tuple(
                definition.finalize(final_context)
                for definition in self.function_definitions
            ),
        )
