import typing
import drip.ops as ops
from drip.basetypes import StackValue, TaggedValue
from drip.program import Program, Subroutine
from drip.interpreter import interpret_subroutine, interpret_program

def interpret_snippet(ops: typing.Tuple[ops.SubroutineOp, ...]) -> StackValue:
    subroutine = Subroutine(ops=ops, arguments=tuple())
    program = Program(subroutines={"main": subroutine})
    return interpret_program(program)


def test_ops_noop() -> None:
    interpret_snippet((ops.NoopOp(),))

def test_opts_two_plus_three_a() -> None:
    result = interpret_snippet(
        (
            ops.PushFromLiteralOp(value=TaggedValue(tag=int, value=2)),
            ops.PushFromLiteralOp(value=TaggedValue(tag=int, value=3)),
            ops.BinaryAddOp(),
            ops.ReturnOp(),
        )
    )
    assert result == TaggedValue(tag=int, value=5)

def test_opts_two_plus_three_b() -> None:
    result = interpret_snippet(
        (
            ops.StoreFromLiteralOp(name="x", value=TaggedValue(tag=int, value=2)),
            ops.StoreFromLiteralOp(name="y", value=TaggedValue(tag=int, value=3)),
            ops.PushFromNameOp(name="x"),
            ops.PushFromNameOp(name="y"),
            ops.BinaryAddOp(),
            ops.ReturnOp(),
        )
    )
    assert result == TaggedValue(tag=int, value=5)

def test_ops_three_times_four() -> None:
    result = interpret_snippet(
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
            ops.PushFromNameOp(name="x"),
            ops.ReturnOp(),
        )
    )
    assert result == TaggedValue(tag=int, value=12)


