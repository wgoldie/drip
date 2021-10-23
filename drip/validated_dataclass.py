import typing
from dataclasses import dataclass


def validated_dataclass(cls: typing.Type) -> typing.Type:
    return dataclass(frozen=True, kw_only=True)(cls)  # type: ignore
