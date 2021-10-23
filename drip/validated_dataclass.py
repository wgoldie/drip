from __future__ import annotations
import typing
from dataclasses import dataclass, Field, fields, MISSING, is_dataclass
import inspect
import abc
from enum import Enum
import traceback

C = typing.TypeVar("C")
T = typing.TypeVar("T")

PRIMITIVES = (str, int, float, bool)


@dataclass(frozen=True)
class ValidationConfig:
    comprehensive: bool


class ValidationNotImplementedError(NotImplementedError):
    pass


def validate_tuple(
    expected_type: typing.Type, value: typing.Any, config: ValidationConfig
) -> None:
    args = typing.get_args(expected_type)
    if not isinstance(value, tuple):
        raise TypeError(
            f"Expected {expected_type} but {value} is of non-tuple type {type(value)}"
        )
    if Ellipsis in args:
        assert len(args) == 2
        subtype = args[0]
        for subvalue in value:
            validate(subtype, subvalue, config)
    else:
        if not len(args) == len(value):
            raise TypeError(
                f"Expected {expected_type} but {value} is of length {len(value)}"
            )
        for subtype, subvalue in zip(args, value):
            validate(subtype, subvalue, config)


def validate_dataclass(
    expected_type: typing.Type, value: typing.Any, config: ValidationConfig
) -> None:
    if not isinstance(value, expected_type):
        raise TypeError(expected_type, value)


def validate_dict(
    expected_type: typing.Type, value: typing.Any, config: ValidationConfig
) -> None:
    if not isinstance(value, dict):
        raise TypeError(
            f"Expected {expected_type} but {value} is of non-dict type {type(value)}"
        )
    args = typing.get_args(expected_type)
    key_type, value_type = args
    for key, subvalue in value.items():
        validate(key_type, key, config)
        validate(value_type, subvalue, config)


def validate_union(
    expected_type: typing.Type, value: typing.Any, config: ValidationConfig
) -> None:
    args = typing.get_args(expected_type)
    for subtype in args:
        exceptions: typing.List[typing.Tuple[Exception, str]] = []
        try:
            validate(subtype, value, config)
            return
        except Exception as e:
            if isinstance(e, ValidationNotImplementedError):
                raise e
            exceptions.append((e, traceback.format_exc()))
    raise TypeError(
        f"{value} could not be parsed as any element of union {expected_type}",
        exceptions,
    )


def validate(
    expected_type: typing.Type, value: typing.Any, config: ValidationConfig
) -> None:

    if expected_type in PRIMITIVES:
        if not isinstance(value, expected_type):
            raise TypeError(
                f"Expected {expected_type} but got {value} of type {type(value)}"
            )
        return

    if expected_type is type(None):
        if value is not None:
            raise TypeError(f"Expected None but got {value}")
        return

    if is_dataclass(expected_type):
        validate_dataclass(expected_type, value, config)
        return

    origin = typing.get_origin(expected_type)

    if is_dataclass(origin):
        # generic dataclasses
        assert origin is not None
        validate_dataclass(origin, value, config)
        return

    if origin is tuple:
        validate_tuple(expected_type, value, config)
        return

    if origin is dict:
        validate_dict(expected_type, value, config)
        return

    if origin is typing.Union:
        validate_union(expected_type, value, config)
        return

    if origin is typing.get_origin(typing.Type):
        args = typing.get_args(expected_type)
        assert len(args) == 1
        if type(args[0]) is typing.TypeVar:
            pass
        elif not value == args[0]:
            raise TypeError(f"Expected {args[0]} but got python type {value}")
        return

    if type(expected_type) is typing.TypeVar:
        return

    if inspect.isclass(expected_type) and (
        issubclass(expected_type, abc.ABC) or issubclass(expected_type, Enum)
    ):
        assert isinstance(value, expected_type)
        return

    if config.comprehensive:
        raise ValidationNotImplementedError(
            f"Expected type {expected_type} (type={type(expected_type)}, origin={origin}, value={value})"
        )


@dataclass
class GlobalValidationConfig:
    validation_enabled: bool


VALIDATION_SETTINGS = GlobalValidationConfig(validation_enabled=False)


def validated_dataclass(cls: typing.Type[C]) -> typing.Type[C]:
    cls = dataclass(frozen=True, kw_only=True)(cls)  # type: ignore
    fields_lookup = {field.name: field for field in fields(cls)}
    class_fields = fields(cls)

    def __init__(self: object, **kwargs: typing.Dict[str, typing.Any]) -> None:
        do_validation = VALIDATION_SETTINGS.validation_enabled
        if do_validation:
            hints = typing.get_type_hints(cls)

        for field in class_fields:
            if field.name in kwargs:
                field_value = kwargs[field.name]
            elif field.default != MISSING:
                field_value = field.default
            elif field.default_factory != MISSING:  # type: ignore
                field_value = field.default_factory()  # type: ignore
            else:
                raise TypeError(f"No argument provided for {field.name}")
            if do_validation:
                validate(
                    hints[field.name], field_value, ValidationConfig(comprehensive=True)
                )
            object.__setattr__(self, field.name, field_value)

    cls.__init__ = __init__  # type: ignore
    return cls
