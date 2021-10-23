from mypy.plugin import Plugin, ClassDefContext
from mypy.nodes import Argument, ARG_NAMED_OPT, ARG_NAMED
from mypy.plugins import dataclasses as dataclasses_plugin
import typing


class CustomDataclassAttribute(dataclasses_plugin.DataclassAttribute):
    def to_argument(self) -> Argument:
        return Argument(
            variable=self.to_var(),
            type_annotation=self.type,
            initializer=None,
            kind=ARG_NAMED_OPT if self.has_default else ARG_NAMED,
        )


def convert_attributes_to_kwonly(
    base_attributes: typing.List[dataclasses_plugin.DataclassAttribute],
) -> typing.Generator[dataclasses_plugin.DataclassAttribute, None, None]:
    for attribute in base_attributes:
        yield CustomDataclassAttribute(
            name=attribute.name,
            is_init_var=attribute.is_init_var,
            is_in_init=attribute.is_in_init,
            has_default=attribute.has_default,
            line=attribute.line,
            column=attribute.column,
            type=attribute.type,
            info=attribute.info,
        )


class CustomDataclassTransformer(dataclasses_plugin.DataclassTransformer):
    def collect_attributes(
        self,
    ) -> typing.Optional[typing.List[dataclasses_plugin.DataclassAttribute]]:
        base_attributes = super(CustomDataclassTransformer, self).collect_attributes()
        if base_attributes is None:
            return None

        return list(convert_attributes_to_kwonly(base_attributes))


def dataclass_class_maker_callback(context: ClassDefContext) -> None:
    transformer = CustomDataclassTransformer(context)
    transformer.transform()


class CustomDataclassesPlugin(Plugin):
    def get_class_decorator_hook(
        self, fullname: str
    ) -> typing.Optional[typing.Callable[[ClassDefContext], None]]:
        if fullname in ("drip.validated_dataclass.validated_dataclass"):
            return dataclass_class_maker_callback
        return None


def plugin(version: str) -> typing.Type[Plugin]:
    VERSIONS = ('0.910',)
    if version not in VERSIONS:
        raise NotImplementedError(f"Mypy version {version} in use. Only versions {VERSIONS} supported")
    return CustomDataclassesPlugin
