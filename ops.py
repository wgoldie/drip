import abc
from dataclasses import dataclass, field, replace
from enum import Enum, auto
import typing
from basetypes import Name, StackValue, ProgramState, TaggedValue
from util import pop, pop_n

def no_default():
    raise ValueError('you must pass a default value for this field')

class OpCode(Enum):
    NOOP = auto()
    STORE_FROM_LITERAL = auto()
    PUSH_FROM_LITERAL = auto()
    PUSH_FROM_NAME = auto()
    POP_TO_NAME = auto()
    BINARY_ADD = auto()
    BINARY_SUBTRACT = auto()
    PRINT_NAME = auto()
    SET_FLAG = auto()
    BRANCH_TO_FLAG = auto()

@dataclass(frozen=True)
class ByteCodeOp(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def parse(cls, ):
        ...


    @abc.abstractmethod
    def interpret(self, state: ProgramState) -> ProgramState:
        ...

@dataclass(frozen=True)
class NoopOp:
    op_code: typing.ClassVar[typing.Literal[OpCode.NOOP]] = OpCode.NOOP
    def interpret(self, state: ProgramState) -> ProgramState:
        return state

@dataclass(frozen=True)
class PushFromNameOp:
    op_code: typing.ClassVar[typing.Literal[OpCode.PUSH_FROM_NAME]] = OpCode.PUSH_FROM_NAME
    name: Name
    def interpret(self, state: ProgramState) -> ProgramState:
        return replace(
            state,
            stack=state.stack + (state.names[self.name],))

@dataclass(frozen=True)
class PopToNameOp:
    op_code: typing.ClassVar[typing.Literal[OpCode.POP_TO_NAME]] = OpCode.POP_TO_NAME
    name: Name
    def interpret(self, state: ProgramState) -> ProgramState:
        popped = pop(state.stack)
        return replace(
            state,
            names={**state.names, self.name: popped.value},
            stack=popped.stack)

@dataclass(frozen=True)
class PushFromLiteralOp:
    op_code: typing.ClassVar[typing.Literal[OpCode.PUSH_FROM_LITERAL]] = OpCode.PUSH_FROM_LITERAL
    value: StackValue
    def interpret(self, state: ProgramState) -> ProgramState:
        return replace(
            state,
            stack=state.stack + (self.value,))

@dataclass(frozen=True)
class StoreFromLiteralOp:
    op_code: typing.ClassVar[typing.Literal[OpCode.STORE_FROM_LITERAL]] = OpCode.STORE_FROM_LITERAL
    name: Name
    value: StackValue

    def interpret(self, state: ProgramState) -> ProgramState:
        return replace(
            state,
            names={**state.names, self.name: self.value})

@dataclass(frozen=True)
class BinaryAddOp:
    op_code: typing.ClassVar[typing.Literal[OpCode.BINARY_ADD]] = OpCode.BINARY_ADD
    def interpret(self, state: ProgramState) -> ProgramState:
        popped = pop_n(state.stack, 2)
        assert isinstance(popped.values[0], TaggedValue) and isinstance(popped.values[1], TaggedValue) and popped.values[0].tag == popped.values[1].tag
        return replace(
            state,
            stack=popped.stack + (TaggedValue(tag=popped.values[0].tag, value=popped.values[0].value + popped.values[1].value),))

@dataclass(frozen=True)
class BinarySubtractOp:
    op_code: typing.ClassVar[typing.Literal[OpCode.BINARY_SUBTRACT]] = OpCode.BINARY_SUBTRACT
    def interpret(self, state: ProgramState) -> ProgramState:
        popped = pop_n(state.stack, 2)
        return replace(
            state,
            stack=popped.stack + (TaggedValue(tag=popped.values[0].tag, value=popped.values[1].value - popped.values[0].value),))

@dataclass(frozen=True)
class PrintNameOp:
    op_code: typing.ClassVar[typing.Literal[OpCode.PRINT_NAME]] = OpCode.PRINT_NAME
    name: Name
    def interpret(self, state: ProgramState) -> ProgramState:
        print(state.names[self.name].value)
        return state

@dataclass(frozen=True)
class SetFlagOp:
    op_code: typing.ClassVar[typing.Literal[OpCode.SET_FLAG]] = OpCode.SET_FLAG
    flag: Name
    def interpret(self, state: ProgramState) -> ProgramState:
        assert self.flag not in state.flags
        return replace(
            state,
            flags={**state.flags, self.flag: state.program_counter})

@dataclass(frozen=True)
class BranchToFlagOp:
    op_code: typing.ClassVar[typing.Literal[OpCode.BRANCH_TO_FLAG]] = OpCode.BRANCH_TO_FLAG
    flag: Name
    def interpret(self, state: ProgramState) -> ProgramState:
        assert self.flag in state.flags
        popped = pop(state.stack)
        return replace(
            state,
            stack=popped.stack,
            program_counter=state.flags[self.flag] if popped.value.value else state.program_counter)
