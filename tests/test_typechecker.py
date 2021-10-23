import typing
import drip.ast as ast
import drip.typecheck as drip_typing
from tests.test_ast import AST_A

FLOAT = drip_typing.ConcreteType(
    type=drip_typing.PrimitiveType(
        primitive=float,
    )
)


def check_expression_in_program(
    expression: ast.Expression,
    structure_definitions: typing.Tuple[
        ast.StructureDefinitionPreliminary, ...
    ] = tuple(),
) -> drip_typing.ExpressionType:
    program_ast = ast.ProgramPreliminary(
        structure_definitions,
        function_definitions=(
            ast.FunctionDefinitionPreliminary(
                name="main",
                arguments=(),
                procedure=(ast.ReturnStatement(expression=expression),),
            ),
        ),
    ).finalize()
    return expression.type_check(
        ast.TypeCheckingContext(structure_lookup=program_ast.structure_lookup)
    )


def test_typing_minimal() -> None:
    expr = ast.LiteralExpression(type_name="Float", value=1.0)
    assert check_expression_in_program(expr) == drip_typing.ConcreteType(
        type=drip_typing.PrimitiveType(primitive=float)
    )


def test_typing_binop() -> None:
    expr = ast.BinaryOperatorExpression(
        operator=ast.BinaryOperator.ADD,
        lhs=ast.LiteralExpression(type_name="Float", value=1.0),
        rhs=ast.LiteralExpression(type_name="Float", value=1.0),
    )
    assert check_expression_in_program(expr) == drip_typing.ConcreteType(
        type=drip_typing.PrimitiveType(primitive=float)
    )


def test_typing_construction() -> None:
    point_ast = ast.StructureDefinitionPreliminary(
        name="Point",
        fields=(
            ast.ArgumentDefinitionPreliminary(name="x", type_name="Float"),
            ast.ArgumentDefinitionPreliminary(name="y", type_name="Float"),
        ),
    )

    expr = ast.ConstructionExpression(
        type_name="Point",
        arguments={
            "x": ast.LiteralExpression(type_name="Float", value=1.0),
            "y": ast.LiteralExpression(type_name="Float", value=1.0),
        },
    )

    point_ast_final = ast.StructureDefinition(
        fields=(
            ast.ArgumentDefinition(name="x", type=FLOAT),
            ast.ArgumentDefinition(name="y", type=FLOAT),
        ),
    )

    assert check_expression_in_program(
        expr, structure_definitions=(point_ast,)
    ) == drip_typing.ConcreteType(
        type=drip_typing.StructureType(structure=point_ast_final)
    )

    expr_2 = ast.PropertyAccessExpression(entity=expr, property_name="x")

    assert check_expression_in_program(
        expr_2, structure_definitions=(point_ast,)
    ) == drip_typing.ConcreteType(
        type=drip_typing.PrimitiveType(primitive=float),
    )


def test_typing_param() -> None:
    param_point_ast = ast.StructureDefinitionPreliminary(
        name="Point",
        type_parameters=("T",),
        fields=(
            ast.ArgumentDefinitionPreliminary(name="x", type_name="T"),
            ast.ArgumentDefinitionPreliminary(name="y", type_name="T"),
        ),
    )
    concrete_point_ast = ast.StructureDefinition(
        fields=(
            ast.ArgumentDefinition(name="x", type=FLOAT),
            ast.ArgumentDefinition(name="y", type=FLOAT),
        ),
    )

    expr = ast.ConstructionExpression(
        type_name="Point",
        type_arguments={"T": "Float"},
        arguments={
            "x": ast.LiteralExpression(type_name="Float", value=1.0),
            "y": ast.LiteralExpression(type_name="Float", value=1.0),
        },
    )

    expr_2 = ast.PropertyAccessExpression(entity=expr, property_name="x")

    check_expression_in_program(expr_2, structure_definitions=(param_point_ast,))

    # drip_typing.ConcreteType(type=drip_typing.StructureType(structure=concrete_point_ast))


def test_full_program() -> None:
    AST_A.finalize().type_check()
