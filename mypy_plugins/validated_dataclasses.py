from mypy.plugin import Plugin, ClassDefContext
import typing

class CustomDataclassesPlugin(Plugin):
    def get_class_decorator_hook(self, fullname: str) -> typing.Optional[typing.Callable[[ClassDefContext], None]]:
        from mypy.plugins import dataclasses
        if fullname in ('drip.validated_dataclass.validated_dataclass'):
            return dataclasses.dataclass_class_maker_callback
        return None


def plugin(version: str) -> typing.Type[Plugin]:
    return CustomDataclassesPlugin
