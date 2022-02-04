from foobartory.core.models.items.bar import Bar
from foobartory.core.models.items.foo import Foo
from foobartory.core.models.items.item import Item


class FooBar(Item):
    foo: Foo
    bar: Bar
