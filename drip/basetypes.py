import typing
from dataclasses import dataclass, field
import drip.ast as ast


T = typing.TypeVar("T")


@dataclass(frozen=True, eq=True)
class TaggedValue(typing.Generic[T]):
    tag_names: typing.ClassVar[typing.Dict[str, typing.Type]] = {
        "int": int,
        "float": float,
    }

    tag: typing.Type[T]
    value: T

    @classmethod
    def parse_asm_literal(
        cls: typing.Type["TaggedValue"], tag_name: str, value_literal: str
    ) -> "TaggedValue":
        tag = cls.tag_names[tag_name]
        return cls(tag=tag, value=tag(value_literal))


StackValue = typing.Union[TaggedValue[float], "StructureInstance"]
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
    def lex_asm(cls: typing.Type["ByteCodeLine"], line: str) -> "ByteCodeLine":
        parts = line.split(" ")
        return cls(op_code=parts[0], arguments=tuple(parts[1:]))


@dataclass(frozen=True)
class FrameState:
    stack: Stack = field(default_factory=tuple)
    names: typing.Dict[Name, StackValue] = field(default_factory=dict)
    return_set: bool = False
    return_value: typing.Optional[StackValue] = None
    flags: typing.Dict[Name, int] = field(default_factory=dict)
    program_counter: int = 0
    structures: typing.Dict[str, ast.StructureDefinition] = field(default_factory=dict)
