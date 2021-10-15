# as close to english/pseudocode as possible
# rigorous: typed, immutable by default
# apis at all layers (bytecode, ast, different syntaxes)
# supports easy (de)serialization of datastructures
from collections import defaultdict
from dataclasses import dataclass, replace, field
import typing
import ops
from basetypes import Name, StackValue, Stack, TaggedValue, FrameState, ByteCodeLine
from program import Program


def interpret_subroutine(program: Program, subroutine: str) -> StackValue:
    lines = program.subroutines[subroutine]
    frame_history = [FrameState()]
    next_state = frame_history[-1]
    while next_state.program_counter < len(lines) and not next_state.return_set:
        line = lines[next_state.program_counter]
        if isinstance(line, ops.SubroutineOp):
            state = line.interpret(next_state)
        elif isinstance(line, ops.CallSubroutineOp):
            result = interpret_subroutine(program, line.name)
            state = replace(next_state, stack=next_state.stack+(result,))
        else:
            raise ValueError(f"Op {op.op_code} not legal inside subroutines")
        frame_history.append(state)
        next_state = replace(state, program_counter=state.program_counter+1)
        # import pprint; pprint.pprint(next_state)
        # import time; time.sleep(0.1)
    return next_state.return_value if next_state.return_value is not None else 0

def interpret_program(program: Program) -> StackValue:
    return interpret_subroutine(program, 'main')
