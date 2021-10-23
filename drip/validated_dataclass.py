import typing
from dataclasses import dataclass

def validated_dataclass(cls: typing.Type) -> typing.Type:
    return dataclass(cls)


