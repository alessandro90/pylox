from numbers import Number
from loxcallable import LoxCallable, LoxInstance

LoxType = Number | str | LoxCallable | LoxInstance | bool | None
