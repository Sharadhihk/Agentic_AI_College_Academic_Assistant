"""Calculator and date-calculation tools (LangChain @tool)."""
import ast
import operator
from datetime import date, datetime, timedelta

from langchain_core.tools import tool

_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def _eval(node):
    """Safely evaluate a math expression AST (no eval())."""
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("Exponent too large")
        return _OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Unsupported expression")


@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression such as '(78*4 + 82*3) / 7'. Useful for CGPA / percentage / attendance."""
    try:
        result = _eval(ast.parse(expression.strip(), mode="eval"))
        return str(round(result, 4))
    except Exception as e:
        return f"Calculation error: {e}"


@tool
def days_until(target_date: str) -> str:
    """Number of days from today until target_date (format YYYY-MM-DD)."""
    try:
        target = datetime.strptime(target_date, "%Y-%m-%d").date()
    except ValueError:
        return "Invalid date. Use YYYY-MM-DD."
    diff = (target - date.today()).days
    weeks = f" (~{diff // 7} weeks {diff % 7} days)" if abs(diff) >= 7 else ""
    if diff >= 0:
        return f"{diff} days remain until {target:%a, %d %b %Y}{weeks}."
    return f"{target:%d %b %Y} was {-diff} days ago."


@tool
def add_days(start_date: str, days: int) -> str:
    """Return the date that is `days` after start_date (YYYY-MM-DD). Negative days go backwards."""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        return "Invalid date. Use YYYY-MM-DD."
    return f"{(start + timedelta(days=int(days))):%a, %d %b %Y}"
