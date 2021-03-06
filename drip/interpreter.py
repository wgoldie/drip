# as close to english/pseudocode as possible
# rigorous: typed, immutable by default
# apis at all layers (bytecode, ast, different syntaxes)
# supports easy (de)serialization of datastructures
from collections import defaultdict
from dataclasses import replace, field
import typing
import drip.ops as ops
from drip.util import pop_n
from drip.basetypes import (
    Name,
    StackValue,
    Stack,
    TaggedValue,
    ByteCodeLine,
)
from drip.program import Program, Subroutine


def interpret_subroutine(
    program: Program, subroutine: Subroutine, init_state: ops.FrameState
) -> StackValue:
    frame_history = [init_state]
    next_state = init_state
    while (
        next_state.program_counter < len(subroutine.ops) and not next_state.return_set
    ):
        line = subroutine.ops[next_state.program_counter]
        if isinstance(line, ops.SubroutineOp):
            state = line.interpret(next_state)
        elif isinstance(line, ops.CallSubroutineOp):
            subsubroutine = program.subroutines[line.name]
            popped = pop_n(next_state.stack, len(subsubroutine.arguments))
            names = {
                argument_name: value
                for argument_name, value in zip(subsubroutine.arguments, popped.values)
            }
            substate = ops.FrameState(names=names, structures=program.structures)
            result = interpret_subroutine(
                program=program, subroutine=subsubroutine, init_state=substate
            )
            state = replace(
                next_state,
                stack=next_state.stack + (result,),
            )
        else:
            raise ValueError(f"Op {line.op_code} not legal inside subroutines")
        frame_history.append(state)
        next_state = replace(state, program_counter=state.program_counter + 1)
        # import pprint; pprint.pprint(next_state)
        # import time; time.sleep(0.1)
    return (
        next_state.return_value
        if next_state.return_value is not None
        else TaggedValue(tag=int, value=0)
    )


def interpret_program(program: Program) -> StackValue:
    return interpret_subroutine(
        program,
        program.subroutines["main"],
        init_state=ops.FrameState(structures=program.structures),
    )
