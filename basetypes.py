import typing
from dataclasses import dataclass, field
import drip_ast as ast


T = typing.TypeVar('T')
C = typing.TypeVar('C')

@dataclass
class TaggedValue(typing.Generic[T]):
    tag_names: typing.ClassVar[typing.Dict[str, typing.Type]] = {
        'int': int,
    }

    tag: typing.Type[T]
    value: T

    @classmethod
    def parse_asm_literal(cls: typing.Type[C], tag_name: str, value_literal: str) -> C:
        tag = cls.tag_names[tag_name]
        return cls(tag=tag, value=tag(value_literal))


StackValue = typing.Union[TaggedValue[int], 'StructureInstance']
Stack = typing.Tuple[StackValue, ...]
OpArg = typing.Union[StackValue]
Name = str


@dataclass
class StructureInstance:
    structure: ast.StructureDefinition
    field_values: typing.Dict[str, StackValue]

@dataclass(frozen=True)
class ByteCodeLine:
    op_code: str
    arguments: typing.Tuple[str, ...]


    @classmethod
    def lex_asm(cls: typing.Type[C], line: str) -> C:
        parts = line.split(' ')
        return cls(op_code=parts[0], arguments=parts[1:])

@dataclass(frozen=True)
class FrameState:
    stack: Stack = field(default_factory=tuple)
    names: typing.Dict[Name, StackValue] = field(default_factory=dict)
    return_set: bool = False
    return_value: typing.Optional[int] = None
    flags: typing.Dict[Name, int] = field(default_factory=dict)
    program_counter: int = 0
    structures: typing.Dict[str, ast.StructureDefinition] = field(default_factory={})
