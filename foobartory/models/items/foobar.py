from foobartory.models.items.bar import Bar
from foobartory.models.items.foo import Foo
from foobartory.models.items.item import Item


class FooBar(Item):
    foo: Foo
    bar: Bar
