import typing
from drip.basetypes import TaggedValue
import drip.ops as ops
from drip.interpreter import interpret_subroutine, interpret_program
from drip.parse_asm import parse_asm_snippet, parse_asm_program
from drip.program import Program, Subroutine
import drip.ast as ast
from drip.compile_ast import compile_ast
from drip.lex import lexer
from drip.parse import parser

PROGRAM_A = """
structure Point (
    x: Float,
    y: Float,
)
"""

PROGRAM_B = """
structure Point (
  x: Float,
  y: Float,
)

structure Line (
  start: Point,
  end: Point,
)

function manhattan_length (line: Line,) -> Float (
  return (line.start.x + line.end.x)+ (line.start.y + line.end.y);
)

function main () -> Int (
  origin = Point(x=0.,y=0.,);
  one_one = Point(x=4.,y=5.,);
  line_a = Line(start=origin, end=one_one,);
  length = manhattan_length(line=line_a,);
  return length;
)

"""


def test_lex_parse_program(program: str) -> None:
    print("lex+parse")
    ast = parser.parse(program)
    print(ast)
    print("compile+run")
    result = interpret_program(compile_ast(ast))
    print("result", result)


def test_lex_parse() -> None:
    # test_lex_parse_program(PROGRAM_A)
    test_lex_parse_program(PROGRAM_B)


def test_ops() -> None:
    def test(ops: typing.Tuple[ops.SubroutineOp, ...]) -> None:
        subroutine = Subroutine(ops=ops, arguments=tuple())
        program = Program(subroutines={"main": subroutine})
        interpret_program(program)

    print("testing ops programs")
    print("noop")
    test((ops.NoopOp(),))
    print("2 + 3 (a)")
    test(
        (
            ops.PushFromLiteralOp(value=TaggedValue(tag=int, value=2)),
            ops.PushFromLiteralOp(value=TaggedValue(tag=int, value=3)),
            ops.BinaryAddOp(),
            ops.PopToNameOp(name="x"),
            ops.PrintNameOp(name="x"),
        )
    )
    print("2 + 3 (b)")
    test(
        (
            ops.StoreFromLiteralOp(name="x", value=TaggedValue(tag=int, value=2)),
            ops.StoreFromLiteralOp(name="y", value=TaggedValue(tag=int, value=3)),
            ops.PushFromNameOp(name="x"),
            ops.PushFromNameOp(name="y"),
            ops.BinaryAddOp(),
            ops.PopToNameOp(name="x"),
            ops.PrintNameOp(name="x"),
        )
    )
    print("3 * 4")
    test(
        (
            ops.StoreFromLiteralOp(name="x", value=TaggedValue(tag=int, value=0)),
            ops.StoreFromLiteralOp(name="c", value=TaggedValue(tag=int, value=3)),
            ops.SetFlagOp(flag="start"),
            ops.PushFromNameOp(name="x"),
            ops.PushFromLiteralOp(value=TaggedValue(tag=int, value=4)),
            ops.BinaryAddOp(),
            ops.PopToNameOp(name="x"),
            ops.PushFromLiteralOp(value=TaggedValue(tag=int, value=1)),
            ops.PushFromNameOp(name="c"),
            ops.BinarySubtractOp(),
            ops.PopToNameOp(name="c"),
            ops.PushFromNameOp(name="c"),
            ops.BranchToFlagOp(flag="start"),
            ops.PrintNameOp(name="x"),
        )
    )


def test_asm_snippets() -> None:
    def test(snippet: str) -> None:
        ops = parse_asm_snippet(snippet)
        subroutine = Subroutine(ops=ops, arguments=tuple())
        program = Program(subroutines={"main": subroutine})
        interpret_program(program)

    print("testing asm programs")
    print("noop")
    test(
        """
    NOOP
    """
    )
    print("2 + 3 (a)")
    test(
        """
    PUSH_FROM_LITERAL int 2
    PUSH_FROM_LITERAL int 3
    BINARY_ADD
    POP_TO_NAME x
    PRINT_NAME x
    """
    )
    print("2 + 3 (b)")
    test(
        """
    STORE_FROM_LITERAL x int 2
    STORE_FROM_LITERAL y int 3
    PUSH_FROM_NAME x
    PUSH_FROM_NAME y
    BINARY_ADD
    POP_TO_NAME z
    PRINT_NAME z
    """
    )
    print("3 * 4")
    test(
        """
        STORE_FROM_LITERAL x int 0
        STORE_FROM_LITERAL c int 3
        SET_FLAG start
        PUSH_FROM_NAME x
        PUSH_FROM_LITERAL int 4
        BINARY_ADD
        POP_TO_NAME x
        PUSH_FROM_LITERAL int 1
        PUSH_FROM_NAME c
        BINARY_SUBTRACT
        POP_TO_NAME c
        PUSH_FROM_NAME c
        BRANCH_TO_FLAG start
        PRINT_NAME x
    """
    )


def test_asm() -> None:
    print("asm prog")
    interpret_program(
        parse_asm_program(
            """
    START_SUBROUTINE main
    STORE_FROM_LITERAL x int 2
    PRINT_NAME x
    END_SUBROUTINE main
    """
        )
    )
    interpret_program(
        parse_asm_program(
            """
    START_SUBROUTINE f
    PUSH_FROM_LITERAL int 4
    RETURN
    END_SUBROUTINE f

    START_SUBROUTINE main
    CALL_SUBROUTINE f
    POP_TO_NAME x
    PRINT_NAME x
    END_SUBROUTINE main
    """
        )
    )

    print("inc 5 twice")
    interpret_program(
        parse_asm_program(
            """
    START_SUBROUTINE inc x
    PUSH_FROM_NAME x
    PUSH_FROM_LITERAL int 1
    BINARY_ADD
    RETURN
    END_SUBROUTINE inc

    START_SUBROUTINE main
    PUSH_FROM_LITERAL int 5
    CALL_SUBROUTINE inc
    POP_TO_NAME x
    PRINT_NAME x
    PUSH_FROM_NAME x
    CALL_SUBROUTINE inc
    POP_TO_NAME x
    PRINT_NAME x

    END_SUBROUTINE main
    """
        )
    )


def test_ast() -> None:
    print("ast")
    ast_a = ast.Program(
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
    print(interpret_program(compile_ast(ast_a)))


if __name__ == "__main__":
    test_lex_parse()
    test_ops()
    test_asm_snippets()
    test_asm()
    test_ast()
