"""Safe calculator: parses the expression with `ast` instead of eval().

Only arithmetic operators, numeric literals, parentheses and a whitelist
of math functions/constants are allowed.
"""

import ast
import math
import operator

_ALLOWED_BINOPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_ALLOWED_UNARYOPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_ALLOWED_FUNCS = {
    "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
    "exp": math.exp, "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "abs": abs, "round": round, "floor": math.floor, "ceil": math.ceil,
    "min": min, "max": max, "sum": sum,
}
_ALLOWED_CONSTS = {"pi": math.pi, "e": math.e, "tau": math.tau}


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        return _ALLOWED_BINOPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS:
        return _ALLOWED_UNARYOPS[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        func = _ALLOWED_FUNCS.get(node.func.id)
        if func is None or node.keywords:
            raise ValueError(f"Function not allowed: {node.func.id}")
        return func(*(_eval(a) for a in node.args))
    if isinstance(node, ast.Name) and node.id in _ALLOWED_CONSTS:
        return _ALLOWED_CONSTS[node.id]
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_eval(e) for e in node.elts]
    raise ValueError(f"Expression not allowed: {ast.dump(node)[:80]}")


def calculate(expression: str) -> float:
    """Evaluate a math expression safely (e.g. 'sqrt(16) + 2**10')."""
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid expression: {exc}") from exc
    result = _eval(tree)
    if isinstance(result, (list, tuple)):
        raise ValueError("Expression must evaluate to a number")
    return result
