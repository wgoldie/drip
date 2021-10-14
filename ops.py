import abc
from dataclasses import dataclass, field, replace
from enum import Enum, auto
import typing
from basetypes import Name, StackValue, ProgramState, TaggedValue, ByteCodeLine
from util import pop, pop_n

def no_default():
    raise ValueError('you must pass a default value for this field')

C = typing.TypeVar('C')

@dataclass(frozen=True)
class ByteCodeOp(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def parse_asm(cls: typing.Type[C], line: ByteCodeLine) -> C:
        ...

    @abc.abstractmethod
    def interpret(self, state: ProgramState) -> ProgramState:
        ...


@dataclass(frozen=True)
class NoopOp:
    op_code: typing.ClassVar[str] = 'NOOP'

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 0
        return cls()

    def interpret(self, state: ProgramState) -> ProgramState:
        return state

@dataclass(frozen=True)
class PushFromNameOp:
    op_code: typing.ClassVar[str] = 'PUSH_FROM_NAME'
    name: Name
    
    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(name=line.arguments[0])

    def interpret(self, state: ProgramState) -> ProgramState:
        return replace(
            state,
            stack=state.stack + (state.names[self.name],))

@dataclass(frozen=True)
class PopToNameOp:
    op_code: typing.ClassVar[str] = 'POP_TO_NAME'
    name: Name
    
    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(name=line.arguments[0])

    def interpret(self, state: ProgramState) -> ProgramState:
        popped = pop(state.stack)
        return replace(
            state,
            names={**state.names, self.name: popped.value},
            stack=popped.stack)

@dataclass(frozen=True)
class PushFromLiteralOp:
    op_code: typing.ClassVar[str] = 'PUSH_FROM_LITERAL'
    value: StackValue

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 2
        return cls(value=TaggedValue.parse_asm_literal(tag_name=line.arguments[0], value_literal=line.arguments[1]))

    def interpret(self, state: ProgramState) -> ProgramState:
        return replace(
            state,
            stack=state.stack + (self.value,))

@dataclass(frozen=True)
class StoreFromLiteralOp:
    op_code: typing.ClassVar[str] = 'STORE_FROM_LITERAL'
    name: Name
    value: StackValue

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 3
        return cls(name=line.arguments[0], value=TaggedValue.parse_asm_literal(tag_name=line.arguments[1], value_literal=line.arguments[2]))

    def interpret(self, state: ProgramState) -> ProgramState:
        return replace(
            state,
            names={**state.names, self.name: self.value})

@dataclass(frozen=True)
class BinaryAddOp:
    op_code: typing.ClassVar[str] = 'BINARY_ADD'

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 0
        return cls()

    def interpret(self, state: ProgramState) -> ProgramState:
        popped = pop_n(state.stack, 2)
        assert isinstance(popped.values[0], TaggedValue) and isinstance(popped.values[1], TaggedValue) and popped.values[0].tag == popped.values[1].tag
        return replace(
            state,
            stack=popped.stack + (TaggedValue(tag=popped.values[0].tag, value=popped.values[0].value + popped.values[1].value),))

@dataclass(frozen=True)
class BinarySubtractOp:
    op_code: typing.ClassVar[str] = 'BINARY_SUBTRACT'

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 0
        return cls()

    def interpret(self, state: ProgramState) -> ProgramState:
        popped = pop_n(state.stack, 2)
        return replace(
            state,
            stack=popped.stack + (TaggedValue(tag=popped.values[0].tag, value=popped.values[1].value - popped.values[0].value),))

@dataclass(frozen=True)
class PrintNameOp:
    op_code: typing.ClassVar[str] = 'PRINT_NAME'
    name: Name
    
    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(name=line.arguments[0])

    def interpret(self, state: ProgramState) -> ProgramState:
        print(state.names[self.name].value)
        return state

@dataclass(frozen=True)
class SetFlagOp:
    op_code: typing.ClassVar[str] = 'SET_FLAG'
    flag: Name
    
    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(flag=line.arguments[0])

    def interpret(self, state: ProgramState) -> ProgramState:
        assert self.flag not in state.flags
        return replace(
            state,
            flags={**state.flags, self.flag: state.program_counter})

@dataclass(frozen=True)
class BranchToFlagOp:
    op_code: typing.ClassVar[str] = 'BRANCH_TO_FLAG'
    flag: Name

    @classmethod
    def parse_asm(cls, line: ByteCodeLine):
        assert cls.op_code == line.op_code
        assert len(line.arguments) == 1
        return cls(flag=line.arguments[0])

    def interpret(self, state: ProgramState) -> ProgramState:
        assert self.flag in state.flags
        popped = pop(state.stack)
        return replace(
            state,
            stack=popped.stack,
            program_counter=state.flags[self.flag] if popped.value.value else state.program_counter)


OPS = (
    NoopOp,
    PushFromNameOp,
    PopToNameOp,
    PushFromLiteralOp,
    StoreFromLiteralOp,
    BinaryAddOp,
    BinarySubtractOp,
    PrintNameOp,
    SetFlagOp,
    BranchToFlagOp)
