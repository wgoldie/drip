# as close to english/pseudocode as possible
# rigorous: typed, immutable by default
# apis at all layers (bytecode, ast, different syntaxes)
from dataclasses import dataclass, replace, field
import typing
import ops
from basetypes import Name, StackValue, Stack, TaggedValue, ProgramState


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

if __name__ == "__main__":
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
