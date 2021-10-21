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


def order_arguments(
    definition: typing.Tuple[ast.ArgumentDefinition, ...],
    values: typing.Dict[str, ast.Expression],
) -> typing.Generator[ast.Expression, None, None]:
    order = {argument.name: i for i, argument in enumerate(definition)}
    ordered_value_entries = sorted(
        list(values.items()), key=lambda value: order[value[0]]
    )
    return (expression for _, expression in ordered_value_entries)


def prepare_stack(
    program: ast.Program,
    expression: ast.Expression,
) -> typing.Tuple[ops.ByteCodeOp, ...]:
    if isinstance(expression, ast.ConstructionExpression):
        structure = program.structure_lookup[expression.type_name]
        return (
            sum(
                (
                    prepare_stack(program, argument_expression)
                    for argument_expression in order_arguments(
                        structure.fields, expression.arguments
                    )
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
        return prepare_stack(program, expression.entity) + (
            ops.PopAndPushPropertyOp(property=expression.property_name),
        )
    elif isinstance(expression, ast.BinaryOperatorExpression):
        return (
            prepare_stack(program, expression.lhs)
            + prepare_stack(program, expression.rhs)
            + operator_ops(expression.operator)
        )
    elif isinstance(expression, ast.FunctionCallExpression):
        function = program.function_lookup[expression.function_name]
        return (
            sum(
                (
                    prepare_stack(program, argument_expression)
                    for argument_expression in order_arguments(
                        function.arguments, expression.arguments
                    )
                ),
                start=tuple(),
            )
            + (ops.CallSubroutineOp(name=expression.function_name),)
        )
    else:
        raise ValueError(f"Expression {expression} has unhandled type")
    return tuple()


def compile_statement_ast(
    program: ast.Program,
    statement: ast.Statement,
) -> typing.Tuple[ops.ByteCodeOp, ...]:
    if isinstance(statement, ast.AssignmentStatement):
        return prepare_stack(program, statement.expression) + (
            ops.PopToNameOp(name=statement.variable_name),
        )
    elif isinstance(statement, ast.ReturnStatement):
        return prepare_stack(program, statement.expression) + (ops.ReturnOp(),)
    else:
        raise ValueError(f"Statement {statement} has unhandled type")


def compile_function_ast(
    program: ast.Program,
    function: ast.FunctionDefinition,
) -> Subroutine:
    return Subroutine(
        ops=sum(
            (
                compile_statement_ast(program, statement)
                for statement in function.procedure
            ),
            start=tuple(),
        ),
        arguments=tuple(argument.name for argument in function.arguments),
    )


def compile_ast(program: ast.Program) -> Program:
    subroutines = {
        function.name: compile_function_ast(program, function)
        for function in program.function_definitions
    }

    assert "main" in subroutines

    return Program(
        subroutines=subroutines,
        structures=program.structure_lookup,
    )
