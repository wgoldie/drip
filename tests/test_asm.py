from drip.parse_asm import parse_asm_snippet, parse_asm_program
from drip.interpreter import interpret_program
from drip.basetypes import StackValue, TaggedValue
from drip.program import Subroutine, Program

def run_asm_snippet(snippet: str) -> StackValue:
    ops = parse_asm_snippet(snippet)
    subroutine = Subroutine(ops=ops, arguments=tuple())
    program = Program(subroutines={"main": subroutine})
    return interpret_program(program)

def test_asm_noop() -> None:
    run_asm_snippet(
        """
    NOOP
    """
    )

def test_two_plus_three_a() -> None:
    result = run_asm_snippet(
        """
    PUSH_FROM_LITERAL int 2
    PUSH_FROM_LITERAL int 3
    BINARY_ADD
    RETURN
    """
    )
    assert result == TaggedValue(tag=int, value=5)

def test_two_plus_three_b() -> None:
    result = run_asm_snippet(
        """
    STORE_FROM_LITERAL x int 2
    STORE_FROM_LITERAL y int 3
    PUSH_FROM_NAME x
    PUSH_FROM_NAME y
    BINARY_ADD
    RETURN
    """
    )
    assert result == TaggedValue(tag=int, value=5)

def test_three_times_four() -> None:
    result = run_asm_snippet(
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
        PUSH_FROM_NAME x
        RETURN
    """
    )
    assert result == TaggedValue(tag=int, value=12)

def test_asm_program_basic() -> None:
    result = interpret_program(
        parse_asm_program(
            """
    START_SUBROUTINE main
    STORE_FROM_LITERAL x int 2
    PUSH_FROM_NAME x
    RETURN
    END_SUBROUTINE main
    """
        )
    )

    assert result == TaggedValue(tag=int, value=2)

def test_asm_program_subroutine() -> None:
    result = interpret_program(
        parse_asm_program(
            """
    START_SUBROUTINE f
    PUSH_FROM_LITERAL int 4
    RETURN
    END_SUBROUTINE f

    START_SUBROUTINE main
    CALL_SUBROUTINE f
    RETURN
    END_SUBROUTINE main
    """
        )
    )
    assert result == TaggedValue(tag=int, value=4)

def test_asm_inc_twice() -> None:
    result = interpret_program(
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
    CALL_SUBROUTINE inc
    RETURN

    END_SUBROUTINE main
    """
        )
    )
    assert result == TaggedValue(tag=int, value = 7)


