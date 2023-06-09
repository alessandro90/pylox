import os
from typing import Callable
import sys


EXPR_IMPORTS = (
    "from __future__ import annotations  # NOTE: No need since python 3.11+\n"
    "from typing import Any, Protocol, TypeVar, runtime_checkable\n"
    "from pyloxtoken import Token\n"
)

STMT_IMPORTS = (
    "from __future__ import annotations  # NOTE: No need since python 3.11+\n"
    "from typing import Protocol, TypeVar, runtime_checkable\n"
    "from pyloxtoken import Token\n"
    "import expr as e\n"
)

EXPRESSION_CLASS_NAME = "Expr"

EXPRESSIONS = {
    "assign": {"name": "Token", "value": EXPRESSION_CLASS_NAME},
    "binary": {
        "left": EXPRESSION_CLASS_NAME,
        "operator": "Token",
        "right": EXPRESSION_CLASS_NAME,
    },
    "call": {
        "callee": EXPRESSION_CLASS_NAME,
        "paren": "Token",
        "arguments": f"list[{EXPRESSION_CLASS_NAME}]",
    },
    "get": {"obj": EXPRESSION_CLASS_NAME, "name": "Token"},
    "grouping": {"expression": EXPRESSION_CLASS_NAME},
    "literal": {"value": "Any"},
    "logical": {
        "left": EXPRESSION_CLASS_NAME,
        "operator": "Token",
        "right": EXPRESSION_CLASS_NAME,
    },
    "set": {
        "obj": EXPRESSION_CLASS_NAME,
        "name": "Token",
        "value": EXPRESSION_CLASS_NAME,
    },
    "super": {"keyword": "Token", "method": "Token"},
    "this": {"keyword": "Token"},
    "unary": {"operator": "Token", "right": EXPRESSION_CLASS_NAME},
    "variable": {"name": "Token"},
}


STATEMENT_CLASS_NAME = "Stmt"
STATEMENTS = {
    "block": {"statements": f"list[{STATEMENT_CLASS_NAME}]"},
    "class": {
        "name": "Token",
        "superclass": "e.Variable | None",
        "methods": "list[Function]",
    },
    "expression": {"expression": f"{'e.'+EXPRESSION_CLASS_NAME}"},
    "function": {
        "name": "Token",
        "params": "list[Token]",
        "body": f"list[{STATEMENT_CLASS_NAME}]",
    },
    "if": {
        "condition": f"e.{EXPRESSION_CLASS_NAME}",
        "then_branch": STATEMENT_CLASS_NAME,
        "else_branch": f"{STATEMENT_CLASS_NAME} | None",
    },
    "print": {"expression": f"{'e.'+EXPRESSION_CLASS_NAME}"},
    "return": {
        "keyword": "Token",
        "value": f"e.{EXPRESSION_CLASS_NAME} | None",
    },
    "var": {
        "name": "Token",
        "initializer": f"{'e.'+EXPRESSION_CLASS_NAME} | None",
    },
    "while": {
        "condition": f"e.{EXPRESSION_CLASS_NAME}",
        "body": STATEMENT_CLASS_NAME,
    },
}

AST = {
    "expr": {
        "classes": EXPRESSIONS,
        "base_name": EXPRESSION_CLASS_NAME,
        "imports": EXPR_IMPORTS,
    },
    "stmt": {
        "classes": STATEMENTS,
        "base_name": STATEMENT_CLASS_NAME,
        "imports": STMT_IMPORTS,
    },
}


NOTE = (
    f"# This file is autogenerated from {os.path.basename(__file__)}\n"
    "# Do not manually change it.\n"
)


GEN_COVAR = "T_co"

T_COV_VAR = f'{GEN_COVAR} = TypeVar("{GEN_COVAR}", covariant=True)'

GEN_INVAR = "T"

T_INV = f'{GEN_INVAR} = TypeVar("{GEN_INVAR}")'


def indent(n=1) -> str:
    return "    " * n


def define_protocol(name: str) -> str:
    text = "@runtime_checkable\n"
    text += f"class {name}(Protocol[{GEN_INVAR}]):\n"
    text += (
        f"{indent()}def accept(self, visitor: Visitor[{GEN_INVAR}])"
        + f" -> {GEN_INVAR}:\n"
        + f"{indent(2)}..."
    )
    text += "\n"
    return text


def add_visitor_method(return_type: str, method: str, category: str) -> str:
    capitelized = method.capitalize()
    return (
        f"{indent()}def {'visit_' + method + '_'}"
        f"{category.lower()}"
        f"(self, {category.lower()}: {capitelized}) -> {return_type}:\n"
        f"{indent(2)}...\n"
    )


def define_visitor(return_type: str, methods: list[str], category: str) -> str:
    text = f"class Visitor(Protocol[{return_type}]):\n"
    for m in methods:
        text += add_visitor_method(return_type, m, category)
        text += "\n"
    return text


def list_fields(fields: dict[str, str]) -> str:
    return ", ".join(
        [f"{name}: {field_type}" for name, field_type in fields.items()]
    )


def define_class(class_name: str, fields: dict[str, str], category: str) -> str:
    text = f"class {class_name.capitalize()}:\n"
    fields_list = list_fields(fields)
    init_paramaters = (
        "self" if not fields_list else f"self, {list_fields(fields)}"
    )
    text += f"{indent()}def __init__({init_paramaters}):\n"
    for name in fields.keys():
        text += f"{indent(2)}self.{name} = {name}\n"
    if not fields.keys():
        text += f"{indent(2)}pass\n"
    text += "\n"
    text += (
        f"{indent()}def accept(self, visitor: Visitor[{GEN_COVAR}])"
        f" -> {GEN_COVAR}:\n"
        f"{indent(2)}return visitor.visit_"
        f"{class_name + '_' + category.lower()}(self)\n"
    )
    return text


def generate(ast: dict) -> str:
    classes = ast["classes"]
    category = ast["base_name"]
    text = NOTE
    text += "\n"
    text += ast["imports"] + "\n\n"
    text += T_COV_VAR + "\n"
    text += T_INV + "\n\n\n"
    text += define_visitor(GEN_COVAR, classes.keys(), category)
    text += "\n"
    text += define_protocol(category)
    text += "\n\n"
    for class_name, fields in classes.items():
        text += define_class(class_name, fields, category)
        text += "\n\n"
    return text[:-2]


def write_file(fname: str, generation_func: Callable):
    with open(fname, "w") as f:
        f.write(generation_func())


if __name__ == "__main__":
    if len(sys.argv) == 1:
        make = ["expr", "stmt"]
    else:
        arg = sys.argv[1]
        assert arg == "expr" or arg == "stmt"
        make = [arg]

    for i in make:
        write_file(
            os.path.join(os.pardir, "pylox", f"{i}.py"),
            lambda: generate(AST[i]),
        )
