# as close to english/pseudocode as possible
# rigorous: typed, immutable by default
# apis at all layers (bytecode, ast, different syntaxes)
from dataclasses import dataclass, replace, field
import typing
import ops
from basetypes import Name, StackValue, Stack, TaggedValue, ProgramState, ByteCodeLine


def interpret(lines: typing.Tuple[ops.ByteCodeOp]) -> int:
    states = [ProgramState()]
    next_state = states[-1]
    while next_state.program_counter < len(lines):
        line = lines[next_state.program_counter]
        state = line.interpret(next_state)
        states.append(state)
        next_state = replace(state, program_counter=state.program_counter+1)
        # import pprint; pprint.pprint(next_state)
        # import time; time.sleep(0.1)
    return next_state.return_value if next_state.return_value is not None else 0

def build_ops_lookup() -> typing.Dict[str, ops.ByteCodeOp]:
    lookup = {}
    for op in ops.OPS:
        assert op.op_code not in lookup
        lookup[op.op_code] = op
    return lookup


def parse_asm(program: str) -> typing.Tuple[ops.ByteCodeOp]:
    ops_lookup = build_ops_lookup()
    raw_lines = program.split('\n')
    clean_lines = (line.strip() for line in raw_lines)
    nonempty_lines = (line for line in clean_lines if len(line) > 0)

    ops = []
    for line in nonempty_lines:
        byte_code_line = ByteCodeLine.lex_asm(line)
        op_type = ops_lookup[byte_code_line.op_code]
        op = op_type.parse_asm(byte_code_line)
        ops.append(op)
    return ops


def test_ops():
    print('testing ops programs')
    print('noop')
    interpret((ops.NoopOp(),))
    print('2 + 3 (a)')
    interpret((
        ops.PushFromLiteralOp(value=TaggedValue(tag=int, value=2)),
        ops.PushFromLiteralOp(value=TaggedValue(tag=int, value=3)),
        ops.BinaryAddOp(),
        ops.PopToNameOp(name='x'),
        ops.PrintNameOp(name='x')
    ))
    print('2 + 3 (b)')
    interpret((
        ops.StoreFromLiteralOp(name = 'x', value=TaggedValue(tag=int, value=2)),
        ops.StoreFromLiteralOp(name='y', value=TaggedValue(tag=int, value=3)),
        ops.PushFromNameOp(name='x'),
        ops.PushFromNameOp(name='y'),
        ops.BinaryAddOp(),
        ops.PopToNameOp(name='x'),
        ops.PrintNameOp(name='x')
    ))
    print('3 * 4')
    interpret((
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



def test_asm():
    print('testing asm programs')
    print('noop')
    interpret(parse_asm('''
    NOOP
    '''))
    print('2 + 3 (a)')
    interpret(parse_asm('''
    PUSH_FROM_LITERAL int 2
    PUSH_FROM_LITERAL int 3
    BINARY_ADD
    POP_TO_NAME x
    PRINT_NAME x
    '''))
    print('2 + 3 (b)')
    interpret(parse_asm('''
    STORE_FROM_LITERAL x int 2
    STORE_FROM_LITERAL y int 3
    PUSH_FROM_NAME x
    PUSH_FROM_NAME y
    BINARY_ADD
    POP_TO_NAME z
    PRINT_NAME z
    '''))
    print('3 * 4')
    interpret(parse_asm('''
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
    '''))

if __name__ == "__main__":
    test_ops()
    test_asm()
