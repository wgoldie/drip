import typing
from drip.parse import parser
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
    type_name: str,
    structure_definitions: typing.Tuple[
        ast.StructureDefinitionPreliminary, ...
    ] = tuple(),
) -> drip_typing.ExpressionType:
    program_ast = ast.ProgramPreliminary(
        structure_definitions=structure_definitions,
        function_definitions=(
            ast.FunctionDefinitionPreliminary(
                name="main",
                arguments=(),
                return_type_name=type_name,
                procedure=(ast.ReturnStatement(expression=expression),),
            ),
        ),
    ).finalize()
    return expression.type_check(
        ast.TypeCheckingContext(structure_lookup=program_ast.structure_lookup)
    )


def test_typing_minimal() -> None:
    expr = ast.LiteralExpression(type_name="Float", value=1.0)
    assert check_expression_in_program(expr, "Float") == drip_typing.ConcreteType(
        type=drip_typing.PrimitiveType(primitive=float)
    )


def test_typing_binop() -> None:
    expr = ast.BinaryOperatorExpression(
        operator=ast.BinaryOperator.ADD,
        lhs=ast.LiteralExpression(type_name="Float", value=1.0),
        rhs=ast.LiteralExpression(type_name="Float", value=1.0),
    )
    assert check_expression_in_program(expr, "Float") == drip_typing.ConcreteType(
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
            ast.ArgumentDefinition(name="x", type=FLOAT, type_name="Float"),
            ast.ArgumentDefinition(name="y", type=FLOAT, type_name="Float"),
        ),
    )

    assert check_expression_in_program(
        expr, "Point", structure_definitions=(point_ast,)
    ) == drip_typing.ConcreteType(
        type=drip_typing.StructureType(structure=point_ast_final)
    )

    expr_2 = ast.PropertyAccessExpression(entity=expr, property_name="x")

    assert check_expression_in_program(
        expr_2, "Float", structure_definitions=(point_ast,)
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
            ast.ArgumentDefinition(name="x", type=FLOAT, type_name="T"),
            ast.ArgumentDefinition(name="y", type=FLOAT, type_name="T"),
        ),
    )

    expr = ast.ConstructionExpression(
        type_name="Point",
        type_arguments={
            "T": "Float",
        },
        arguments={
            "x": ast.LiteralExpression(type_name="Float", value=1.0),
            "y": ast.LiteralExpression(type_name="Float", value=1.0),
        },
    )

    assert check_expression_in_program(
        expr, "Point", structure_definitions=(param_point_ast,)
    ) == drip_typing.ConcreteType(
        type=drip_typing.StructureType(structure=concrete_point_ast)
    )

    expr_2 = ast.PropertyAccessExpression(entity=expr, property_name="x")

    assert (
        check_expression_in_program(
            expr_2, "Float", structure_definitions=(param_point_ast,)
        )
        == FLOAT
    )


def test_typing_param_parse() -> None:
    ast_a = parser.parse(
        """
    structure Point [T, U] (
      x: T,
      y: U 
    )

    function main () -> Float (
      origin = Point [T = Float, U = Float] (x=0.,y=0.,);
      return origin.x;
    )

    """
    ).finalize()
    context = ast.TypeCheckingContext(structure_lookup=ast_a.structure_lookup)
    assert ast_a.function_definitions[0].type_check(context) == FLOAT


def test_full_program() -> None:
    AST_A.finalize().type_check()
