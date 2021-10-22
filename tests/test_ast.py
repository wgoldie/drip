from drip.basetypes import TaggedValue
import drip.ast as ast
from drip.interpreter import interpret_subroutine, interpret_program
from drip.compile_ast import compile_ast

AST_A = ast.Program(
        structure_definitions=(
            ast.StructureDefinition(
                name="Point",
                fields=(
                    ast.ArgumentDefinition(name="x", type_name="float"),
                    ast.ArgumentDefinition(name="y", type_name="float"),
                ),
            ),
            ast.StructureDefinition(
                name="Line",
                fields=(
                    ast.ArgumentDefinition(name="start", type_name="Point"),
                    ast.ArgumentDefinition(name="end", type_name="Point"),
                ),
            ),
        ),
        function_definitions=(
            ast.FunctionDefinition(
                name="manhattan_length",
                arguments=(ast.ArgumentDefinition(name="line", type_name="Line"),),
                procedure=(
                    ast.ReturnStatement(
                        expression=ast.BinaryOperatorExpression(
                            operator=ast.BinaryOperator.ADD,
                            lhs=ast.BinaryOperatorExpression(
                                operator=ast.BinaryOperator.ADD,
                                lhs=ast.PropertyAccessExpression(
                                    entity=ast.PropertyAccessExpression(
                                        entity=ast.VariableReferenceExpression(
                                            name="line"
                                        ),
                                        property_name="start",
                                    ),
                                    property_name="x",
                                ),
                                rhs=ast.PropertyAccessExpression(
                                    entity=ast.PropertyAccessExpression(
                                        entity=ast.VariableReferenceExpression(
                                            name="line"
                                        ),
                                        property_name="end",
                                    ),
                                    property_name="x",
                                ),
                            ),
                            rhs=ast.BinaryOperatorExpression(
                                operator=ast.BinaryOperator.ADD,
                                lhs=ast.PropertyAccessExpression(
                                    entity=ast.PropertyAccessExpression(
                                        entity=ast.VariableReferenceExpression(
                                            name="line"
                                        ),
                                        property_name="start",
                                    ),
                                    property_name="y",
                                ),
                                rhs=ast.PropertyAccessExpression(
                                    entity=ast.PropertyAccessExpression(
                                        entity=ast.VariableReferenceExpression(
                                            name="line"
                                        ),
                                        property_name="end",
                                    ),
                                    property_name="y",
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            ast.FunctionDefinition(
                name="main",
                arguments=tuple(),
                procedure=(
                    ast.AssignmentStatement(
                        variable_name="origin",
                        expression=ast.ConstructionExpression(
                            type_name="Point",
                            arguments={
                                "x": ast.LiteralExpression(value=0.0),
                                "y": ast.LiteralExpression(value=0.0),
                            },
                        ),
                    ),
                    ast.AssignmentStatement(
                        variable_name="one_one",
                        expression=ast.ConstructionExpression(
                            type_name="Point",
                            arguments={
                                "x": ast.LiteralExpression(value=1.0),
                                "y": ast.LiteralExpression(value=1.0),
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
    result = interpret_program(compile_ast(AST_A))
    assert result == TaggedValue(tag=float, value=2)


