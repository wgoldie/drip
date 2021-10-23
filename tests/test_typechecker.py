import typing
import drip.ast as ast
import drip.typecheck as drip_typing
from tests.test_ast import AST_A

def check_expression_in_program(expression: ast.Expression, structure_definitions: typing.Tuple[ast.StructureDefinition, ...] = tuple()) -> drip_typing.ExpressionType:
    program_ast = ast.Program(
        structure_definitions,
        function_definitions=(
            ast.FunctionDefinition(
                name='main',
                arguments=(),
                procedure=(
                    ast.ReturnStatement(
                        expression=expression
                        ),
                )

            ),
        ))
    return expression.type_check(ast.TypeCheckingContext(program=program_ast))


def test_typing_minimal() -> None:
    expr = ast.LiteralExpression(type_name='float', value=1.0)
    assert check_expression_in_program(expr) ==\
        drip_typing.ConcreteType(type=drip_typing.PrimitiveType(primitive=float))


def test_typing_binop() -> None:
    expr = ast.BinaryOperatorExpression(
        operator=ast.BinaryOperator.ADD,
        lhs=ast.LiteralExpression(type_name='float', value=1.0),
        rhs=ast.LiteralExpression(type_name='float', value=1.0),
    )
    assert check_expression_in_program(expr) ==\
        drip_typing.ConcreteType(type=drip_typing.PrimitiveType(primitive=float))


def test_typing_construction() -> None:
    point_ast = ast.StructureDefinition(
                name="Point",
                fields=(
                    ast.ArgumentDefinition(name="x", type_name="float"),
                    ast.ArgumentDefinition(name="y", type_name="float"),
                ),
            )

    expr = ast.ConstructionExpression(
        type_name='Point',
        arguments={
            'x': ast.LiteralExpression(type_name='float', value=1.0),
            'y': ast.LiteralExpression(type_name='float', value=1.0),
        }
    )

    assert check_expression_in_program(expr, structure_definitions=(point_ast,)) ==\
        drip_typing.ConcreteType(type=drip_typing.StructureType(structure_name='Point'))

    expr_2 = ast.PropertyAccessExpression(
        entity=expr,
        property_name='x'
    )
   
    assert check_expression_in_program(expr_2, structure_definitions=(point_ast,)) ==\
        drip_typing.ConcreteType(type=drip_typing.PrimitiveType(primitive=float),
    )


def test_full_program() -> None:
    AST_A.type_check()
