import ops
import typing
from basetypes import TaggedValue
from interpreter import interpret_subroutine, interpret_program
from parse import parse_asm_snippet, parse_asm_program
from program import Program, Subroutine


def test_ops():
    def test(ops: typing.Tuple[ops.SubroutineOp]):
        subroutine = Subroutine(ops=ops, arguments=tuple())
        program = Program(subroutines={'main': subroutine})
        interpret_program(program)

    print('testing ops programs')
    print('noop')
    sr1 = test((ops.NoopOp(),))
    print('2 + 3 (a)')
    test((
        ops.PushFromLiteralOp(value=TaggedValue(tag=int, value=2)),
        ops.PushFromLiteralOp(value=TaggedValue(tag=int, value=3)),
        ops.BinaryAddOp(),
        ops.PopToNameOp(name='x'),
        ops.PrintNameOp(name='x')
    ))
    print('2 + 3 (b)')
    test((
        ops.StoreFromLiteralOp(name = 'x', value=TaggedValue(tag=int, value=2)),
        ops.StoreFromLiteralOp(name='y', value=TaggedValue(tag=int, value=3)),
        ops.PushFromNameOp(name='x'),
        ops.PushFromNameOp(name='y'),
        ops.BinaryAddOp(),
        ops.PopToNameOp(name='x'),
        ops.PrintNameOp(name='x')
    ))
    print('3 * 4')
    test((
        ops.StoreFromLiteralOp(name = 'x', value=TaggedValue(tag=int, value=0)),
        ops.StoreFromLiteralOp(name='c', value=TaggedValue(tag=int, value=3)),
        ops.SetFlagOp(flag='start'),
        ops.PushFromNameOp(name='x'),
        ops.PushFromLiteralOp(value=TaggedValue(tag=int, value=4)),
        ops.BinaryAddOp(),
        ops.PopToNameOp(name='x'),
        ops.PushFromLiteralOp(value=TaggedValue(tag=int, value=1)),
        ops.PushFromNameOp(name='c'),
        ops.BinarySubtractOp(),
        ops.PopToNameOp(name='c'),
        ops.PushFromNameOp(name='c'),
        ops.BranchToFlagOp(flag='start'),
        ops.PrintNameOp(name='x')
    ))



def test_asm_snippets():
    def test(snippet: str):
        ops = parse_asm_snippet(snippet)
        subroutine = Subroutine(ops=ops, arguments=tuple())
        program = Program(subroutines={'main': subroutine})
        interpret_program(program)
    print('testing asm programs')
    print('noop')
    test('''
    NOOP
    ''')
    print('2 + 3 (a)')
    test('''
    PUSH_FROM_LITERAL int 2
    PUSH_FROM_LITERAL int 3
    BINARY_ADD
    POP_TO_NAME x
    PRINT_NAME x
    ''')
    print('2 + 3 (b)')
    test('''
    STORE_FROM_LITERAL x int 2
    STORE_FROM_LITERAL y int 3
    PUSH_FROM_NAME x
    PUSH_FROM_NAME y
    BINARY_ADD
    POP_TO_NAME z
    PRINT_NAME z
    ''')
    print('3 * 4')
    test('''
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
    ''')


def test_asm():
    print('asm prog')
    interpret_program(parse_asm_program('''
    START_SUBROUTINE main
    STORE_FROM_LITERAL x int 2
    PRINT_NAME x
    END_SUBROUTINE main
    '''))
    interpret_program(parse_asm_program('''
    START_SUBROUTINE f
    PUSH_FROM_LITERAL int 4
    RETURN
    END_SUBROUTINE f

    START_SUBROUTINE main
    CALL_SUBROUTINE f
    POP_TO_NAME x
    PRINT_NAME x
    END_SUBROUTINE main
    '''))

    print('inc 5 twice')
    interpret_program(parse_asm_program('''
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
    '''))

if __name__ == "__main__":
    test_ops()
    test_asm_snippets()
    test_asm()
