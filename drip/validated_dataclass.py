import typing
from dataclasses import dataclass, Field, fields, MISSING


C = typing.TypeVar("C")
T = typing.TypeVar("T")

PRIMITIVES = (str, int, float)


@dataclass(frozen=True)
class ValidationConfig:
    comprehensive: bool


def validate(type: typing.Type, value: typing.Any, config: ValidationConfig) -> None:
    if type in PRIMITIVES:
        assert isinstance(value, type)
        return
    origin = typing.get_origin(type)
    args = typing.get_args(type)
    if origin is tuple:
        assert isinstance(value, tuple)
        if Ellipsis in args:
            assert len(args) == 2
            subtype = args[0]
            for subvalue in value:
                validate(subtype, subvalue, config)
        else:
            assert len(args) == len(value)
            for subtype, subvalue in zip(args, value):
                validate(subtype, subvalue, config)
        return
    if config.comprehensive:
        raise NotImplementedError(type)


def validated_dataclass(cls: typing.Type[C]) -> typing.Type[C]:
    cls = dataclass(frozen=True, kw_only=True)(cls)  # type: ignore
    fields_lookup = {field.name: field for field in fields(cls)}
    class_fields = fields(cls)

    def __init__(self: object, **kwargs: typing.Dict[str, typing.Any]) -> None:
        for field in class_fields:
            if field.name in kwargs:
                field_value = kwargs[field.name]
            elif field.default != MISSING:
                field_value = field.default
            elif field.default_factory != MISSING:  # type: ignore
                field_value = field.default_factory()  # type: ignore
            else:
                raise TypeError(f"No argument provided for {field.name}")
            validate(field.type, field_value, ValidationConfig(comprehensive=False))
            object.__setattr__(self, field.name, field_value)

    cls.__init__ = __init__  # type: ignore
    return cls
