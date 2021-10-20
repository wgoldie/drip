import abc
from dataclasses import dataclass, field, replace
from enum import Enum, auto
import typing
from drip.basetypes import (
    Name,
    StackValue,
    FrameState,
    TaggedValue,
    ByteCodeLine,
    StructureInstance,
)
from drip.util import pop, pop_n


def no_default():
    raise ValueError("you must pass a default value for this field")


C = typing.TypeVar("C")


@dataclass(frozen=True)
class ByteCodeOp(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def parse_asm(cls: typing.Type[C], line: ByteCodeLine) -> C:
        ...


@dataclass(frozen=True)
class StartSubroutineOp(ByteCodeOp):
    op_code: typing.ClassVar[str] = "START_SUBROUTINE"
    name: Name
    arguments: typing.Tuple[str]

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) >= 1
        return cls(name=line.arguments[0], arguments=line.arguments[1:])


@dataclass(frozen=True)
class EndSubroutineOp(ByteCodeOp):
    op_code: typing.ClassVar[str] = "END_SUBROUTINE"
    name: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(name=line.arguments[0])


@dataclass(frozen=True)
class CallSubroutineOp(ByteCodeOp):
    op_code: typing.ClassVar[str] = "CALL_SUBROUTINE"
    name: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(name=line.arguments[0])


@dataclass(frozen=True)
class SubroutineOp(ByteCodeOp, abc.ABC):
    @abc.abstractmethod
    def interpret(self, state: FrameState) -> FrameState:
        ...


@dataclass(frozen=True)
class ReturnOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "RETURN"

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 0
        return cls()

    def interpret(self, state: FrameState) -> FrameState:
        assert state.return_set is False
        popped = pop(state.stack)
        return replace(
            state, return_value=popped.value, return_set=True, stack=popped.stack
        )


@dataclass(frozen=True)
class NoopOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "NOOP"

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 0
        return cls()

    def interpret(self, state: FrameState) -> FrameState:
        return state


@dataclass(frozen=True)
class PushFromNameOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "PUSH_FROM_NAME"
    name: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(name=line.arguments[0])

    def interpret(self, state: FrameState) -> FrameState:
        return replace(state, stack=state.stack + (state.names[self.name],))


@dataclass(frozen=True)
class PopToNameOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "POP_TO_NAME"
    name: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(name=line.arguments[0])

    def interpret(self, state: FrameState) -> FrameState:
        popped = pop(state.stack)
        return replace(
            state, names={**state.names, self.name: popped.value}, stack=popped.stack
        )


@dataclass(frozen=True)
class PushFromLiteralOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "PUSH_FROM_LITERAL"
    value: StackValue

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 2
        return cls(
            value=TaggedValue.parse_asm_literal(
                tag_name=line.arguments[0], value_literal=line.arguments[1]
            )
        )

    def interpret(self, state: FrameState) -> FrameState:
        return replace(state, stack=state.stack + (self.value,))


@dataclass(frozen=True)
class StoreFromLiteralOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "STORE_FROM_LITERAL"
    name: Name
    value: StackValue

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
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


@dataclass(frozen=True)
class BinaryAddOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "BINARY_ADD"

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
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


@dataclass(frozen=True)
class BinarySubtractOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "BINARY_SUBTRACT"

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 0
        return cls()

    def interpret(self, state: FrameState) -> FrameState:
        popped = pop_n(state.stack, 2)
        return replace(
            state,
            stack=popped.stack
            + (
                TaggedValue(
                    tag=popped.values[0].tag,
                    value=popped.values[1].value - popped.values[0].value,
                ),
            ),
        )


@dataclass(frozen=True)
class PrintNameOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "PRINT_NAME"
    name: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(name=line.arguments[0])

    def interpret(self, state: FrameState) -> FrameState:
        print(state.names[self.name].value)
        return state


@dataclass(frozen=True)
class ConstructStructureOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "CONSTRUCT_STRUCTURE"
    structure: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(name=line.arguments[0])

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


@dataclass(frozen=True)
class PopAndPushPropertyOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "POP_AND_PUSH_PROPERTY"
    property: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(name=line.arguments[0])

    def interpret(self, state: FrameState) -> FrameState:
        popped = pop(stack=state.stack)
        assert isinstance(popped.value, StructureInstance)

        return replace(
            state,
            stack=popped.stack + (popped.value.field_values[self.property],),
        )


@dataclass(frozen=True)
class SetFlagOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "SET_FLAG"
    flag: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(flag=line.arguments[0])

    def interpret(self, state: FrameState) -> FrameState:
        assert self.flag not in state.flags
        return replace(state, flags={**state.flags, self.flag: state.program_counter})


@dataclass(frozen=True)
class BranchToFlagOp(SubroutineOp):
    op_code: typing.ClassVar[str] = "BRANCH_TO_FLAG"
    flag: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(flag=line.arguments[0])

    def interpret(self, state: FrameState) -> FrameState:
        assert self.flag in state.flags
        popped = pop(state.stack)
        return replace(
            state,
            stack=popped.stack,
            program_counter=state.flags[self.flag]
            if popped.value.value
            else state.program_counter,
        )


OPS = (
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
