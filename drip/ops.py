import abc
from dataclasses import field, replace
from enum import Enum, auto
import typing
import drip.ast as ast
from drip.basetypes import (
    Name,
    Stack,
    StackValue,
    TaggedValue,
    ByteCodeLine,
    FrameState,
    StructureInstance,
)
from drip.validated_dataclass import validated_dataclass
from drip.util import pop, pop_n


def no_default() -> None:
    raise ValueError("you must pass a default value for this field")


C = typing.TypeVar("C")


class ByteCodeOp(abc.ABC):
    op_code: typing.ClassVar[str]

    @classmethod
    @abc.abstractmethod
    def parse_asm(cls: typing.Type[C], line: ByteCodeLine) -> C:
        ...


@validated_dataclass
class StartSubroutineOp(ByteCodeOp):
    op_code: typing.ClassVar[str] = "START_SUBROUTINE"
    name: Name
    arguments: typing.Tuple[str, ...]

    @classmethod
    def parse_asm(cls, line: ByteCodeLine) -> "StartSubroutineOp":
        assert cls.op_code == line.op_code
        assert len(line.arguments) >= 1
        return cls(name=line.arguments[0], arguments=line.arguments[1:])


@validated_dataclass
class EndSubroutineOp(ByteCodeOp):
    op_code: typing.ClassVar[str] = "END_SUBROUTINE"
    name: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine) -> "EndSubroutineOp":
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(name=line.arguments[0])


@validated_dataclass
class CallSubroutineOp(ByteCodeOp):
    op_code: typing.ClassVar[str] = "CALL_SUBROUTINE"
    name: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine) -> "CallSubroutineOp":
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(name=line.arguments[0])


class SubroutineOp(ByteCodeOp, abc.ABC):
    @abc.abstractmethod
    def interpret(self, state: FrameState) -> FrameState:
        ...


@validated_dataclass
class ReturnOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "RETURN"

    @classmethod
    def parse_asm(cls, line: ByteCodeLine) -> "ReturnOp":
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 0
        return cls()

    def interpret(self, state: FrameState) -> FrameState:
        assert state.return_set is False
        popped = pop(state.stack)
        return replace(
            state, return_value=popped.value, return_set=True, stack=popped.stack
        )


@validated_dataclass
class NoopOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "NOOP"

    @classmethod
    def parse_asm(cls, line: ByteCodeLine) -> "NoopOp":
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 0
        return cls()

    def interpret(self, state: FrameState) -> FrameState:
        return state


@validated_dataclass
class PushFromNameOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "PUSH_FROM_NAME"
    name: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine) -> "PushFromNameOp":
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(name=line.arguments[0])

    def interpret(self, state: FrameState) -> FrameState:
        return replace(state, stack=state.stack + (state.names[self.name],))


@validated_dataclass
class PopToNameOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "POP_TO_NAME"
    name: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine) -> "PopToNameOp":
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(name=line.arguments[0])

    def interpret(self, state: FrameState) -> FrameState:
        popped = pop(state.stack)
        return replace(
            state, names={**state.names, self.name: popped.value}, stack=popped.stack
        )


@validated_dataclass
class PushFromLiteralOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "PUSH_FROM_LITERAL"
    value: StackValue

    @classmethod
    def parse_asm(cls, line: ByteCodeLine) -> "PushFromLiteralOp":
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 2
        return cls(
            value=TaggedValue.parse_asm_literal(
                tag_name=line.arguments[0], value_literal=line.arguments[1]
            )
        )

    def interpret(self, state: FrameState) -> FrameState:
        return replace(state, stack=state.stack + (self.value,))


@validated_dataclass
class StoreFromLiteralOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "STORE_FROM_LITERAL"
    name: Name
    value: StackValue

    @classmethod
    def parse_asm(cls, line: ByteCodeLine) -> "StoreFromLiteralOp":
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 3
        return cls(
            name=line.arguments[0],
            value=TaggedValue.parse_asm_literal(
                tag_name=line.arguments[1], value_literal=line.arguments[2]
            ),
        )

    def interpret(self, state: FrameState) -> FrameState:
        return replace(state, names={**state.names, self.name: self.value})


@validated_dataclass
class BinaryAddOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "BINARY_ADD"

    @classmethod
    def parse_asm(cls, line: ByteCodeLine) -> "BinaryAddOp":
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 0
        return cls()

    def interpret(self, state: FrameState) -> FrameState:
        popped = pop_n(state.stack, 2)
        assert (
            isinstance(popped.values[0], TaggedValue)
            and isinstance(popped.values[1], TaggedValue)
            and popped.values[0].tag == popped.values[1].tag
        )
        return replace(
            state,
            stack=popped.stack
            + (
                TaggedValue(
                    tag=popped.values[0].tag,
                    value=popped.values[0].value + popped.values[1].value,
                ),
            ),
        )


@validated_dataclass
class BinarySubtractOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "BINARY_SUBTRACT"

    @classmethod
    def parse_asm(cls, line: ByteCodeLine) -> "BinarySubtractOp":
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 0
        return cls()

    def interpret(self, state: FrameState) -> FrameState:
        popped = pop_n(state.stack, 2)
        lhs = popped.values[1]
        rhs = popped.values[0]
        assert isinstance(lhs, TaggedValue)
        assert isinstance(rhs, TaggedValue)
        return replace(
            state,
            stack=popped.stack
            + (
                TaggedValue(
                    tag=lhs.tag,
                    value=lhs.value - rhs.value,
                ),
            ),
        )


@validated_dataclass
class PrintNameOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "PRINT_NAME"
    name: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine) -> "PrintNameOp":
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(name=line.arguments[0])

    def interpret(self, state: FrameState) -> FrameState:
        print(state.names[self.name])
        return state


@validated_dataclass
class ConstructStructureOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "CONSTRUCT_STRUCTURE"
    structure: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine) -> "ConstructStructureOp":
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(structure=line.arguments[0])

    def interpret(self, state: FrameState) -> FrameState:
        structure = state.structures[self.structure]
        popped = pop_n(stack=state.stack, n=len(structure.fields))
        instance = StructureInstance(
            structure=structure,
            field_values={
                field.name: value
                for field, value in zip(structure.fields, popped.values)
            },
        )

        return replace(
            state,
            stack=popped.stack + (instance,),
        )


@validated_dataclass
class PopAndPushPropertyOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "POP_AND_PUSH_PROPERTY"
    property: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine) -> "PopAndPushPropertyOp":
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(property=line.arguments[0])

    def interpret(self, state: FrameState) -> FrameState:
        popped = pop(stack=state.stack)
        assert isinstance(popped.value, StructureInstance)

        return replace(
            state,
            stack=popped.stack + (popped.value.field_values[self.property],),
        )


@validated_dataclass
class SetFlagOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "SET_FLAG"
    flag: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine) -> "SetFlagOp":
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(flag=line.arguments[0])

    def interpret(self, state: FrameState) -> FrameState:
        assert self.flag not in state.flags
        return replace(state, flags={**state.flags, self.flag: state.program_counter})


@validated_dataclass
class BranchToFlagOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "BRANCH_TO_FLAG"
    flag: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine) -> "BranchToFlagOp":
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(flag=line.arguments[0])

    def interpret(self, state: FrameState) -> FrameState:
        assert self.flag in state.flags
        popped = pop(state.stack)
        assert isinstance(popped.value, TaggedValue)
        print(popped.value)
        return replace(
            state,
            stack=popped.stack,
            program_counter=state.flags[self.flag]
            if popped.value.value
            else state.program_counter,
        )


OPS: typing.Tuple[typing.Type[ByteCodeOp], ...] = (
    StartSubroutineOp,
    EndSubroutineOp,
    CallSubroutineOp,
    NoopOp,
    PushFromNameOp,
    PopToNameOp,
    PushFromLiteralOp,
    StoreFromLiteralOp,
    BinaryAddOp,
    BinarySubtractOp,
    PrintNameOp,
    SetFlagOp,
    BranchToFlagOp,
    ReturnOp,
    ConstructStructureOp,
    PopAndPushPropertyOp,
)
