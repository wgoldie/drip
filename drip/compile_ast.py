import typing
import drip.ast as ast
from drip.basetypes import TaggedValue
from drip.program import Program, Subroutine
import drip.ops as ops


def operator_ops(operator: ast.BinaryOperator) -> typing.Tuple[ops.ByteCodeOp, ...]:
    if operator == ast.BinaryOperator.ADD:
        return (ops.BinaryAddOp(),)
    elif operator == ast.BinaryOperator.SUBTRACT:
        return (ops.BinarySubtractOp(),)
    else:
        raise ValueError(f"Unhandled operator {operator}")


def prepare_stack(expression: ast.Expression) -> typing.Tuple[ops.ByteCodeOp, ...]:
    if isinstance(expression, ast.ConstructionExpression):
        # need to fix out of order keywords
        return (
            sum(
                (
                    prepare_stack(argument_expression)
                    for argument_expression in expression.arguments.values()
                ),
                start=tuple(),
            )
            + (ops.ConstructStructureOp(structure=expression.type_name),)
        )
    elif isinstance(expression, ast.VariableReferenceExpression):
        return (ops.PushFromNameOp(name=expression.name),)
    elif isinstance(expression, ast.LiteralExpression):
        return (
            ops.PushFromLiteralOp(value=TaggedValue(tag=float, value=expression.value)),
        )
    elif isinstance(expression, ast.PropertyAccessExpression):
        return prepare_stack(expression.entity) + (
            ops.PopAndPushPropertyOp(property=expression.property_name),
        )
    elif isinstance(expression, ast.BinaryOperatorExpression):
        return (
            prepare_stack(expression.lhs)
            + prepare_stack(expression.rhs)
            + operator_ops(expression.operator)
        )
    elif isinstance(expression, ast.FunctionCallExpression):
        # need to fix out of order kwargs
        return sum(
            (
                prepare_stack(argument_expression)
                for argument_expression in expression.arguments.values()
            ),
            start=tuple(),
        ) + (ops.CallSubroutineOp(name=expression.function_name),)
    else:
        raise ValueError(f"Expression {expression} has unhandled type")
    return tuple()


def compile_statement_ast(
    statement: ast.Statement,
) -> typing.Tuple[ops.ByteCodeOp, ...]:
    if isinstance(statement, ast.AssignmentStatement):
        return prepare_stack(statement.expression) + (
            ops.PopToNameOp(name=statement.variable_name),
        )
    elif isinstance(statement, ast.ReturnStatement):
        return prepare_stack(statement.expression) + (ops.ReturnOp(),)
    else:
        raise ValueError(f"Statement {statement} has unhandled type")


def compile_function_ast(
    function: ast.FunctionDefinition,
    structure_lookup: typing.Dict[str, ast.StructureDefinition],
) -> Subroutine:
    return Subroutine(
        ops=sum(
            (compile_statement_ast(statement) for statement in function.procedure),
            start=tuple(),
        ),
        arguments=tuple(argument.name for argument in function.arguments),
    )


def compile_ast(program: ast.Program) -> Program:
    structure_lookup = {
        structure_definition.name: structure_definition
        for structure_definition in program.structure_definitions
    }

    subroutines = {
        function.name: compile_function_ast(function, structure_lookup)
        for function in program.function_definitions
    }

    assert "main" in subroutines

    return Program(
        subroutines=subroutines,
        structures=structure_lookup,
    )
