from drip.basetypes import TaggedValue
from drip.parse import parser
from drip.interpreter import interpret_subroutine, interpret_program
from drip.compile_ast import compile_ast

LINE_PROGRAM = """
    structure Point (
      x: Float,
      y: Float
    )

    structure Line (
      start: Point,
      end: Point,
    )

    function manhattan_length (line: Line) -> Float (
      a = (line.start.x + line.end.x);
      b = (line.start.y + line.end.y);
      return a + b;
    )

    function main () -> Float (
      origin = Point(x=0.,y=0.,);
      one_one = Point(x=4.,y=5.,);
      line_a = Line(start=origin, end=one_one,);
      length = manhattan_length(line=line_a,);
      return length;
    )

    """


def test_lex_parse_basic() -> None:
    ast = parser.parse(
        """
        structure Point (
            x: Float,
            y: Float,
        )
    """
    ).finalize()
    assert ast.structure_lookup["Point"] is not None


def test_lex_parse_line() -> None:
    ast = parser.parse(LINE_PROGRAM).finalize()

    result = interpret_program(compile_ast(ast))
    assert result == TaggedValue(tag=float, value=9)
