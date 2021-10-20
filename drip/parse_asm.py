import typing
from collections import defaultdict
import drip.ops as ops
from drip.basetypes import ByteCodeLine
from drip.program import Program, Subroutine


def build_ops_lookup() -> typing.Dict[str, ops.ByteCodeOp]:
    lookup = {}
    for op in ops.OPS:
        assert op.op_code not in lookup
        lookup[op.op_code] = op
    return lookup


def lex_program(program: str):
    ops_lookup = build_ops_lookup()
    raw_lines = program.split("\n")
    for line in raw_lines:
        clean_line = line.strip()
        if len(clean_line) == 0:
            continue
        byte_code_line = ByteCodeLine.lex_asm(clean_line)
        op_type = ops_lookup[byte_code_line.op_code]
        op = op_type.parse_asm(byte_code_line)
        yield op


def parse_asm_snippet(program: str) -> typing.Tuple[ops.ByteCodeOp, ...]:
    return list(lex_program(program))


def parse_asm_program(program: str) -> Program:
    subroutines = {}
    current_subroutine = None
    current_ops = []
    for op in lex_program(program):
        if isinstance(op, ops.StartSubroutineOp):
            if current_subroutine is not None:
                raise ValueError("Started a subroutine inside a subroutine")
            else:
                current_subroutine = op
        elif isinstance(op, ops.EndSubroutineOp):
            if current_subroutine is None:
                raise ValueError("Ended a subroutine not inside a subroutine")
            else:
                assert (
                    current_subroutine.name == op.name
                ), f"ended subroutine {op.name} inside subroutine {current_subroutine}"
                subroutines[current_subroutine.name] = Subroutine(
                    ops=current_ops, arguments=current_subroutine.arguments
                )
                current_subroutine = None
                current_ops = []
        elif current_subroutine is not None:
            current_ops.append(op)
        else:
            raise ValueError(f"Illegal line {line} outside of subroutine")
    assert subroutines["main"] is not None, "no main subroutine"
    return Program(subroutines=subroutines)
