from __future__ import annotations

import ast
import math
from datetime import datetime, timezone
from typing import Any

from langchain_core.tools import tool


class _SafeEval(ast.NodeVisitor):
    """
    Tiny, safe arithmetic evaluator.

    Supports numbers, parentheses, + - * / // % **, and a few math functions.
    """

    _binops = {
        ast.Add: lambda a, b: a + b,
        ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b,
        ast.Div: lambda a, b: a / b,
        ast.FloorDiv: lambda a, b: a // b,
        ast.Mod: lambda a, b: a % b,
        ast.Pow: lambda a, b: a**b,
    }
    _unaryops = {ast.UAdd: lambda a: +a, ast.USub: lambda a: -a}
    _names: dict[str, Any] = {
        "pi": math.pi,
        "e": math.e,
        "sqrt": math.sqrt,
        "log": math.log,
        "log10": math.log10,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "abs": abs,
        "round": round,
    }

    def visit(self, node: ast.AST) -> Any:  # type: ignore[override]
        if isinstance(node, ast.Expression):
            return self.visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in self._binops:
            return self._binops[type(node.op)](self.visit(node.left), self.visit(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in self._unaryops:
            return self._unaryops[type(node.op)](self.visit(node.operand))
        if isinstance(node, ast.Name) and node.id in self._names:
            return self._names[node.id]
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in self._names:
            fn = self._names[node.func.id]
            args = [self.visit(a) for a in node.args]
            return fn(*args)
        raise ValueError("Unsupported expression")


def _safe_eval(expr: str) -> float:
    tree = ast.parse(expr, mode="eval")
    return float(_SafeEval().visit(tree))


@tool
def calculator(expression: str) -> str:
    """Evaluate a simple arithmetic expression and return the numeric result."""
    try:
        value = _safe_eval(expression.strip())
        if value.is_integer():
            return str(int(value))
        return str(value)
    except Exception as e:
        return f"ERROR: {e}"


@tool
def now_utc() -> str:
    """Return the current UTC time in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()

