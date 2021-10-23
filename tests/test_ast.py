from drip.basetypes import TaggedValue
import drip.ast as ast
from drip.interpreter import interpret_subroutine, interpret_program
from drip.compile_ast import compile_ast

AST_A = ast.ProgramPreliminary(
    structure_definitions=(
        ast.StructureDefinitionPreliminary(
            name="Point",
            fields=(
                ast.ArgumentDefinitionPreliminary(name="x", type_name="Float"),
                ast.ArgumentDefinitionPreliminary(name="y", type_name="Float"),
            ),
        ),
        ast.StructureDefinitionPreliminary(
            name="Line",
            fields=(
                ast.ArgumentDefinitionPreliminary(name="start", type_name="Point"),
                ast.ArgumentDefinitionPreliminary(name="end", type_name="Point"),
            ),
        ),
    ),
    function_definitions=(
        ast.FunctionDefinitionPreliminary(
            name="manhattan_length",
            arguments=(
                ast.ArgumentDefinitionPreliminary(name="line", type_name="Line"),
            ),
            procedure=(
                ast.ReturnStatement(
                    expression=ast.BinaryOperatorExpression(
                        operator=ast.BinaryOperator.ADD,
                        lhs=ast.BinaryOperatorExpression(
                            operator=ast.BinaryOperator.ADD,
                            lhs=ast.PropertyAccessExpression(
                                entity=ast.PropertyAccessExpression(
                                    entity=ast.VariableReferenceExpression(name="line"),
                                    property_name="start",
                                ),
                                property_name="x",
                            ),
                            rhs=ast.PropertyAccessExpression(
                                entity=ast.PropertyAccessExpression(
                                    entity=ast.VariableReferenceExpression(name="line"),
                                    property_name="end",
                                ),
                                property_name="x",
                            ),
                        ),
                        rhs=ast.BinaryOperatorExpression(
                            operator=ast.BinaryOperator.ADD,
                            lhs=ast.PropertyAccessExpression(
                                entity=ast.PropertyAccessExpression(
                                    entity=ast.VariableReferenceExpression(name="line"),
                                    property_name="start",
                                ),
                                property_name="y",
                            ),
                            rhs=ast.PropertyAccessExpression(
                                entity=ast.PropertyAccessExpression(
                                    entity=ast.VariableReferenceExpression(name="line"),
                                    property_name="end",
                                ),
                                property_name="y",
                            ),
                        ),
                    ),
                ),
            ),
        ),
        ast.FunctionDefinitionPreliminary(
            name="main",
            arguments=tuple(),
            procedure=(
                ast.AssignmentStatement(
                    variable_name="origin",
                    expression=ast.ConstructionExpression(
                        type_name="Point",
                        arguments={
                            "x": ast.LiteralExpression(type_name="Float", value=0.0),
                            "y": ast.LiteralExpression(type_name="Float", value=0.0),
                        },
                    ),
                ),
                ast.AssignmentStatement(
                    variable_name="one_one",
                    expression=ast.ConstructionExpression(
                        type_name="Point",
                        arguments={
                            "x": ast.LiteralExpression(type_name="Float", value=1.0),
                            "y": ast.LiteralExpression(type_name="Float", value=1.0),
                        },
                    ),
                ),
                ast.AssignmentStatement(
                    variable_name="line_a",
                    expression=ast.ConstructionExpression(
                        type_name="Line",
                        arguments={
                            "start": ast.VariableReferenceExpression(name="origin"),
                            "end": ast.VariableReferenceExpression(name="one_one"),
                        },
                    ),
                ),
                ast.AssignmentStatement(
                    variable_name="l",
                    expression=ast.FunctionCallExpression(
                        function_name="manhattan_length",
                        arguments={
                            "line": ast.VariableReferenceExpression(name="line_a"),
                        },
                    ),
                ),
                ast.ReturnStatement(
                    expression=ast.VariableReferenceExpression(name="l"),
                ),
            ),
        ),
    ),
)


def test_ast() -> None:
    result = interpret_program(compile_ast(AST_A.finalize()))
    assert result == TaggedValue(tag=float, value=2)
