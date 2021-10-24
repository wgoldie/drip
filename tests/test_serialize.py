from tests.test_lex_parse import LINE_PROGRAM
from drip.parse import parser


def test_serialize() -> None:
    ast_1 = parser.parse(LINE_PROGRAM).finalize()
    program_text = ast_1.serialize()
    ast_2 = parser.parse(program_text).finalize()
    assert ast_1 == ast_2
